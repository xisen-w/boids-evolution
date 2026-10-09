import json
import re
from pathlib import Path

from .hostio import archive_rejected, remove_workspace_entry, write_feedback
from .model import AgentPortModel
from .registry import LocalSociety, Registry
from .sandbox import run_agent, stop

MENUS = [
    [
        "Read CSV/JSONL across partitions with schema and missing-value handling",
        "Compose row filtering, column selection, derived columns and sorting",
        "Normalize and parse dates and times with explicit errors",
        "Grouped aggregation and custom reductions",
    ],
    [
        "Keyed joins and reconciliation with duplicate and missing keys",
        "Ranking, lags and rolling windows within groups",
        "Reuse or repair previously published interfaces",
        "Write deterministic typed CSV/JSONL/Parquet outputs",
    ],
    [
        "Combine IO, grouping and time operations into useful workflows",
        "Support schema alignment, missing values and clear diagnostics",
        "Repair, extend or replace tools with edge-case tests",
        "Simplify common downstream use without forcing a particular API",
    ],
]


def evidence(society, author, round_, visible):
    cards = [society.registry.artifacts[i] for i in sorted(visible)]
    neighbor_cards = [c for c in cards if c["author"] in society.neighbors(author)]
    pairs = []
    for i, a in enumerate(neighbor_cards):
        for b in neighbor_cards[i + 1 :]:
            x, y = (set(re.findall(r"\w+", c["description"].lower())) for c in (a, b))
            pairs.append((len(x & y) / max(1, len(x | y)), a["id"], b["id"]))
    return dict(
        similar_description_pairs=sorted(pairs, reverse=True)[:2],
        recent_neighbor_tools=[
            c["id"] for c in sorted(neighbor_cards, key=lambda c: (-c["round"], c["id"]))[:4]
        ],
        neighbor_last_round_declared_capabilities=[
            c["capabilities"] for c in neighbor_cards if c["round"] == round_ - 1
        ],
        caveat="Syntax and author descriptions are not semantic correctness. AST size is only a complexity proxy.",
    )


def build_society(
    root: Path, tasks: Path, image: str, budget, key: str, condition: str, n=4, rounds=3, steps=6, seed=7108
):
    registry = Registry(root / "registry")
    society = LocalSociety(registry, n, condition, seed)
    (root / "config.json").write_text(
        json.dumps(
            dict(
                condition=condition,
                agents=n,
                rounds=rounds,
                step_limit=steps,
                ring=society.ring,
                seed=seed,
                protocol="v0.2-dependency-bundles",
            ),
            indent=2,
        )
    )
    specification = (tasks / "pyda/design/instruction.md").read_text()
    # Keep semantic requirements but replace the original single-library packaging instructions.
    specification = specification.split("## General instructions")[0]
    outcomes = []
    for round_ in range(1, rounds + 1):
        publications = []
        # Snapshot all views before any agent starts. Sequential dispatch does not leak same-round work.
        views = {a: society.view(a, round_) for a in society.agents}
        for author in society.agents:
            slot = root / "builders" / author / f"round-{round_:02d}"
            slot.mkdir(parents=True)
            workspace = root / "private" / author
            workspace.mkdir(parents=True, exist_ok=True)
            candidate = workspace / "candidate"
            remove_workspace_entry(candidate)
            visible = views[author]
            library = registry.materialize(visible, slot / "view")
            local_evidence = evidence(society, author, round_, visible)
            rules = (
                "S: consider avoiding redundant capability construction; repair remains allowed. "
                "A: consider reusing useful neighbor interfaces and implementations; syntax is not correctness. "
                "C: consider how your contribution fits the recent needs and activity of your neighbors."
                if condition == "local-boids"
                else "Choose a useful contribution from the shared opportunities. You may build, repair, reuse or skip. "
                "Use the available evidence as you judge appropriate."
            )
            prompt = f"""Build reusable Python capabilities for the following continuing library ecosystem.
{specification}
Common opportunities this round (identical for all builders):
{json.dumps(MENUS[(round_ - 1) % len(MENUS)])}
Your publication namespace will be published.{author}_r{round_:02d}.
Your own private files persist in /workspace. Received immutable packages and full README/API documentation are under /library/published. See /library/catalogue.json. PYTHONPATH=/library.
Publish ONE package at /workspace/candidate with __init__.py, README.md describing exact API signatures/examples/limitations, and publish.json containing description (string), capabilities (list of activity labels), dependencies (list of received published IDs you actually reference). You may use multiple .py files, design any native Python API, implement a whole workflow, repair previous work, or reuse packages with `from published.ID import ...`. Do not import a package not in the catalogue. A package and its explicitly declared frozen dependencies will be shared together. Maximum 64 files / 300 KB. Do not add unrelated files.
Test your contribution with python before submitting. For candidate imports, use `PYTHONPATH=/workspace:/library python ...`. Other authors' candidates and all downstream evaluation files are unavailable. Alternatively write /workspace/SKIP with a reason and no candidate.
Local evidence: {json.dumps(local_evidence)}
Guidance: {rules}
"""
            (slot / "prompt.txt").write_text(prompt)
            skip = workspace / "SKIP"
            skip.unlink(missing_ok=True)
            model = AgentPortModel(key, budget, f"{condition}/{author}/r{round_}")
            agent, env = run_agent(model, workspace, library, slot / "trajectory.json", image, steps)
            try:
                execution = agent.run(prompt)
            finally:
                stop(env)
            result = dict(
                author=author,
                round=round_,
                execution=execution,
                visible=sorted(visible),
                public_status="not_semantically_verified",
            )
            if skip.exists() and not candidate.exists():
                result["publication_status"] = "skip"
            else:
                try:
                    identity = registry.publish(author, round_, candidate, allowed=visible)
                    publications.append(identity)
                    result.update(publication_status="published", id=identity)
                except (OSError, ValueError, SyntaxError, KeyError) as exc:
                    result.update(publication_status="publication_contract_failure", error=str(exc))
                    result["rejection_archive"] = archive_rejected(candidate, slot / "rejected-candidate")
            (slot / "result.json").write_text(json.dumps(result, indent=2))
            write_feedback(workspace, result)
            outcomes.append(result)
            print(
                json.dumps(
                    dict(
                        condition=condition,
                        author=author,
                        round=round_,
                        publication=result["publication_status"],
                        calls=budget.calls,
                    )
                ),
                flush=True,
            )
        society.deliver(round_, publications)
        (root / "receipts.json").write_text(json.dumps(society.receipts, indent=2))
    frozen = registry.freeze(root / "frozen")
    (root / "builders.json").write_text(json.dumps(outcomes, indent=2))
    return frozen
