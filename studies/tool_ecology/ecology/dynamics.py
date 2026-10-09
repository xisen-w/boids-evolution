"""Exploratory repeated-demand ecology with mini-SWE-agent and verified feedback."""

import argparse
import importlib.metadata
import json
import re
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import workload
from .dynamics_metrics import summarize
from .hostio import archive_rejected, remove_workspace_entry, write_feedback
from .images import resolve_image
from .model import AgentPortModel, Budget
from .registry import LocalSociety, Registry, file_hashes
from .sandbox import run_agent, stop
from .services import judge
from .study import evidence

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parents[1]


def is_cross(edge):
    match = re.fullmatch(r"published\.(a\d{2})_r\d+(?:\.[^.]+)*->published\.(a\d{2})_r\d+\..+", edge)
    return bool(match and match[1] != match[2])


def service_evidence(result):
    verified = sorted(f for f, stats in result["families"].items() if stats["passed"] == stats["total"])
    correct = [item for item in result["details"] if item["correct"]]
    cross = sorted({edge for item in correct for edge in item["executed_edges"] if is_cross(edge)})
    verified_cross = sorted(
        {
            edge
            for item in correct
            if item["family"] in verified
            for edge in item["executed_edges"]
            if is_cross(edge)
        }
    )
    return dict(
        verified_families=verified,
        cross_author_edges=cross,
        verified_cross_author_edges=verified_cross,
        correct_cross_author_requests=sum(
            any(is_cross(e) for e in item["executed_edges"]) for item in correct
        ),
        correct_service_requests=len(correct),
        total_service_requests=len(result["details"]),
    )


def build_prompt(author, round_, condition, local):
    guidance = (
        "S: consider avoiding redundant construction when a useful neighbor capability exists; repair is allowed. "
        "A: consider reusing verified useful neighbor interfaces; syntax and a declaration alone are not correctness. "
        "C: consider how your contribution fits recurring service needs and the recent capabilities of your neighbors."
        if condition == "local-boids"
        else "Choose useful contributions from the common service opportunities. You may build, repair, reuse or skip; judge the available evidence yourself."
    )
    return f"""You are one role-free software agent in a continuing tool ecosystem. All agents receive these SAME recurring service opportunities; no specialist roles are assigned. Build or maintain useful reusable Python capabilities; choose which opportunities to serve. You may specialize or build general capabilities. Correctness, maintaining useful capabilities, and avoiding unnecessary reimplementation matter. Do not claim capabilities you have not tested.
Round {round_}. Your new immutable publication will be published.{author}_r{round_:02d}.
Private /workspace files persist. Received immutable packages/README/API examples are under /library/published, and /library/catalogue.json records their declared interfaces and verified DEV service feedback. PYTHONPATH=/library. Import previously received tools with `from published.ID import ...`. A package plus all explicitly declared dependencies travels together to neighbors next round. Your view is a pre-round snapshot. You cannot see other private work or same-round publications.

Recurring service families (choose one or several to serve):
{json.dumps(workload.FAMILIES, indent=2)}
Input rows are list[dict] with id(float), region(str or None), product(str), date(ISO YYYY-MM-DD), units(float or None), price_cents(float or None), cost_cents(float). Lookup rows contain region, target(float or None), manager(str). Empty tables, missing values, odd capitalization/whitespace, unknown regions and zero targets are valid. request includes fill (zero/mean/median), agg (sum/mean/count), window (2/3/4); functions must honor varying parameters and not mutate rows, lookup or request. Equality checks retain all specified keys and row order (numeric tolerance 1e-6). For median with even count use the average of central values. All-missing fill is 0. Group count counts nonmissing revenue, not group rows.

Publish ONE native Python package at /workspace/candidate with __init__.py and README.md documenting exact public APIs/examples/limitations. You may use any internal/native API, classes and modules. Include publish.json: {{"description":"...", "capabilities":["..."], "dependencies":["received_ID"], "checks":{{"family_name":"top_level_callable_name"}}}}. Each checks callable is a thin service adapter at the package root taking (rows, lookup, request) and returning that family's full output. checks can list one or several of the six families; adapters may call your arbitrary internal APIs or received packages. Only list actually implemented families. Do not import unreceived tools. Max 64 files / 300 KB. Test with Python before submission (PYTHONPATH=/workspace:/library for candidate imports). You can instead write /workspace/SKIP with a reason and no candidate. Independent host service tests run only after your session and return aggregate per-family feedback next round; their data/reference code are unavailable. Service feedback is DEV, not sealed external benchmark performance.
Local evidence: {json.dumps(local)}
Guidance: {guidance}
"""


def usage(budget):
    result = dict(physical_requests=budget.calls, input_tokens=0, output_tokens=0, cached_tokens=0, errors=0)
    for file in budget.root.glob("response-*.json"):
        response = json.loads(file.read_text())
        result["errors"] += int("error_type" in response)
        tokens = response.get("usage") or {}
        for key in ("input_tokens", "output_tokens"):
            result[key] += tokens.get(key, 0)
        result["cached_tokens"] += (tokens.get("input_tokens_details") or {}).get("cached_tokens", 0)
    return result


def run_society(root, condition, image, key, *, seed, n, rounds, steps, workers):
    root.mkdir(parents=True)
    budget = Budget(root / "api", call_limit=n * rounds * steps, output_limit=n * rounds * steps * 3000)
    registry = Registry(root / "registry")
    society = LocalSociety(registry, n, condition, seed)
    (root / "config.json").write_text(
        json.dumps(
            dict(
                condition=condition,
                seed=seed,
                agents=n,
                rounds=rounds,
                steps=steps,
                workers=workers,
                ring=society.ring,
                protocol="v0.3.1-repeated-demand-entry-attribution",
            ),
            indent=2,
        )
    )
    records = []
    try:
        for round_ in range(1, rounds + 1):
            jobs = []
            for author in society.agents:
                slot = root / "builders" / author / f"round-{round_:02d}"
                slot.mkdir(parents=True)
                workspace = root / "private" / author
                workspace.mkdir(parents=True, exist_ok=True)
                remove_workspace_entry(workspace / "candidate")
                remove_workspace_entry(workspace / "SKIP")
                visible = society.view(author, round_)
                view = registry.materialize(visible, slot / "view")
                local = evidence(society, author, round_, visible)
                local["verified_service_feedback"] = [
                    {
                        k: registry.artifacts[i].get(k)
                        for k in ("id", "author", "checks", "verified_families", "service_counts")
                    }
                    for i in sorted(visible)
                ]
                prompt = build_prompt(author, round_, condition, local)
                (slot / "prompt.txt").write_text(prompt)
                jobs.append((author, slot, workspace, view, visible, prompt))

            def execute(job):
                author, slot, workspace, view, visible, prompt = job
                model = AgentPortModel(key, budget, f"{condition}/seed-{seed}/{author}/r{round_}")
                agent, env = run_agent(model, workspace, view, slot / "trajectory.json", image, steps)
                try:
                    execution = agent.run(prompt)
                finally:
                    stop(env)
                return execution

            with ThreadPoolExecutor(max_workers=workers) as executor:
                executions = list(executor.map(execute, jobs))
            # All model turns finish before publication/evaluation/delivery. Ordering is deterministic.
            publications = []
            for job, execution in zip(jobs, executions):
                author, slot, workspace, view, visible, _ = job
                candidate = workspace / "candidate"
                row = dict(
                    author=author,
                    round=round_,
                    execution=execution,
                    visible=sorted(visible),
                    verified_families=[],
                    cross_author_edges=[],
                )
                if (workspace / "SKIP").exists() and not candidate.exists():
                    row["publication_status"] = "skip"
                else:
                    try:
                        identity = registry.publish(
                            author, round_, candidate, allowed=visible, allowed_checks=set(workload.FAMILIES)
                        )
                    except (OSError, ValueError, SyntaxError, KeyError) as exc:
                        row.update(
                            publication_status="publication_contract_failure",
                            error=str(exc),
                            rejection_archive=archive_rejected(candidate, slot / "rejected-candidate"),
                        )
                    else:
                        row.update(publication_status="published", id=identity)
                        artifact = registry.artifacts[identity]
                        library = registry.materialize({identity}, slot / "judge-view")
                        result = judge(library, artifact, slot / "service", image, seed=seed, round_=round_)
                        observed = service_evidence(result)
                        verified = observed["verified_families"]
                        row.update(
                            **observed,
                            service_counts=result["families"],
                            declared_dependencies=artifact["dependencies"],
                        )
                        artifact.update(verified_families=verified, service_counts=result["families"])
                        (registry.root / f"{identity}.json").write_text(json.dumps(artifact, indent=2))
                        publications.append(identity)
                (slot / "result.json").write_text(json.dumps(row, indent=2))
                write_feedback(workspace, row)
                records.append(row)
                (root / "records.json").write_text(json.dumps(records, indent=2))
                (root / "summary.json").write_text(json.dumps(summarize(records), indent=2))
                print(
                    json.dumps(
                        dict(
                            condition=condition,
                            seed=seed,
                            author=author,
                            round=round_,
                            status=row["publication_status"],
                            verified=row["verified_families"],
                            correct_cross_edges=len(row["cross_author_edges"]),
                            requests=budget.calls,
                        )
                    ),
                    flush=True,
                )
            society.deliver(round_, publications)
            (root / "receipts.json").write_text(json.dumps(society.receipts, indent=2))
            if usage(budget)["errors"]:
                raise RuntimeError("API failure: society invalid; do not reinterpret as task failure")
        registry.freeze(root / "frozen")
        return summarize(records)
    finally:
        (root / "usage.json").write_text(json.dumps(usage(budget), indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=Path("/tmp/boids-agentport.key"))
    parser.add_argument("--image", default="boids-pyda:20261008")
    parser.add_argument("--agents", type=int, default=8)
    parser.add_argument("--rounds", type=int, default=6)
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seeds", default="71,108,2026")
    parser.add_argument("--arms", default="local-neutral,local-boids,independent")
    parser.add_argument("--phase", choices=["engineering", "exploratory"], required=True)
    args = parser.parse_args()
    arms, seeds = args.arms.split(","), [int(s) for s in args.seeds.split(",")]
    if (
        len(set(arms)) != len(arms)
        or set(arms) - {"local-neutral", "local-boids", "independent"}
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("invalid/duplicate arms or seeds")
    if args.agents < 3 or min(args.rounds, args.steps, args.workers) < 1 or args.workers > 4:
        raise ValueError("invalid execution sizing")
    if args.output.exists():
        raise ValueError("output exists; no silent resume or overwrite")
    revision = subprocess.check_output(["git", "-C", str(CORE), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "-C", str(CORE), "status", "--porcelain"], text=True):
        raise RuntimeError("commit exact source before paid run")
    image = resolve_image(args.image)
    args.output.mkdir(parents=True)
    manifest = dict(
        protocol="v0.3.1-repeated-demand-entry-attribution",
        classification=args.phase,
        code_revision=revision,
        image=image,
        parameters={
            k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k != "key_file"
        },
        source_hashes={k: v for k, v in file_hashes(ROOT / "ecology").items() if k.endswith(".py")},
        reference_hashes={k: v for k, v in file_hashes(CORE / "boidsnet/env").items() if k.endswith(".py")},
        mini_swe_version=importlib.metadata.version("mini-swe-agent"),
        openai_version=importlib.metadata.version("openai"),
        provider_money_cost="unverified",
        maximum_requests=len(arms) * len(seeds) * args.agents * args.rounds * args.steps,
    )
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    key = args.key_file.read_text().strip()
    all_results = []
    try:
        for seed in seeds:
            # Counterbalance arm order across seeds; no scientific cell is rerun after seeing a score.
            order = arms[seeds.index(seed) % len(arms) :] + arms[: seeds.index(seed) % len(arms)]
            for condition in order:
                root = args.output / f"seed-{seed}" / condition
                result = run_society(
                    root,
                    condition,
                    image,
                    key,
                    seed=seed,
                    n=args.agents,
                    rounds=args.rounds,
                    steps=args.steps,
                    workers=args.workers,
                )
                all_results.append(dict(condition=condition, seed=seed, **result))
                (args.output / "summary.json").write_text(json.dumps(all_results, indent=2))
        (args.output / "COMPLETE.json").write_text(
            json.dumps(dict(societies=len(all_results), status="complete"), indent=2)
        )
    except BaseException as exc:
        (args.output / "ABORTED.json").write_text(
            json.dumps(
                dict(error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc()),
                indent=2,
            )
        )
        raise


if __name__ == "__main__":
    main()
