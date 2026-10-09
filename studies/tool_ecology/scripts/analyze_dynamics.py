"""Archive society results; replay instrumentation and intervene on observed edges.

All diagnostics are separate from original scored publications. No model calls.
"""

import argparse
import csv
import json
import shutil
from pathlib import Path

from studies.tool_ecology.scripts.collection_provenance import cell_provenance, usage_accounting

from ecology.dynamics import is_cross
from ecology.registry import Registry
from ecology.services import judge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnostics", action="store_true")
    parser.add_argument("--edge-limit", type=int, default=12)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output exists; preserve earlier diagnostics")
    if not (args.run / "COMPLETE.json").exists():
        raise ValueError("batch incomplete; do not report as complete experiment")
    args.output.mkdir(parents=True)
    manifest = json.loads((args.run / "manifest.json").read_text())
    shutil.copyfile(args.run / "manifest.json", args.output / "manifest.json")
    shutil.copyfile(args.run / "summary.json", args.output / "summary.json")
    if (args.run / "COLLECTION.json").exists():
        shutil.copyfile(args.run / "COLLECTION.json", args.output / "COLLECTION.json")
    table, diagnostics = [], []
    for society in sorted(args.run.glob("seed-*/*")):
        if not (society / "records.json").exists():
            continue
        seed = int(society.parent.name.split("-")[1])
        condition = society.name
        summary = json.loads((society / "summary.json").read_text())
        records = json.loads((society / "records.json").read_text())
        config = json.loads((society / "config.json").read_text())
        usage = json.loads((society / "usage.json").read_text())
        frozen = society / "frozen"
        Registry.verify_freeze(frozen)
        dest = args.output / society.parent.name / condition
        dest.mkdir(parents=True)
        for name in ("records.json", "summary.json", "config.json", "usage.json", "receipts.json"):
            shutil.copyfile(society / name, dest / name)
        if (society / "generation-manifest.json").exists():
            shutil.copyfile(society / "generation-manifest.json", dest / "generation-manifest.json")
        shutil.copytree(frozen, dest / "frozen")
        rounds = []
        for rnd in range(1, config["rounds"] + 1):
            selected = [r for r in records if r["round"] <= rnd]
            from ecology.dynamics_metrics import summarize

            rounds.append(dict(round=rnd, **summarize(selected)))
        (dest / "round-metrics.json").write_text(json.dumps(rounds, indent=2))
        table.append(
            dict(
                seed=seed,
                condition=condition,
                **cell_provenance(manifest, f"{society.parent.name}/{condition}"),
                publications=summary["publications"],
                declared_six_service_publications=sum(
                    r["publication_status"] == "published" and len(r.get("service_counts", {})) == 6
                    for r in records
                ),
                declared_single_service_publications=sum(
                    r["publication_status"] == "published" and len(r.get("service_counts", {})) == 1
                    for r in records
                ),
                round_one_declared_six_service_publications=sum(
                    r["round"] == 1
                    and r["publication_status"] == "published"
                    and len(r.get("service_counts", {})) == 6
                    for r in records
                ),
                correct_publications=summary["correct_publications"],
                coverage=len(summary["verified_family_coverage"]),
                complete_six_publications=sum(len(r["verified_families"]) == 6 for r in records),
                strict_claimed_publications=sum(
                    bool(r.get("service_counts"))
                    and all(v["passed"] == v["total"] for v in r["service_counts"].values())
                    for r in records
                ),
                correct_cross_author_requests=summary["correct_cross_author_requests"],
                correct_service_requests=summary["correct_service_requests"],
                total_declared_service_requests=summary["total_service_requests"],
                redundant_author_family_pairs=summary["redundant_author_family_pairs"],
                mean_author_profile_jaccard=summary["mean_author_profile_jaccard"],
                sustained_specialists=len(summary["sustained_specialists"]),
                correct_cross_author_publications=summary["correct_cross_author_publications"],
                observed_cross_author_edges=len(summary["observed_cross_author_edges"]),
                **usage,
            )
        )
        if not args.diagnostics:
            continue
        diag = society / "diagnostics-v03"
        if diag.exists():
            raise ValueError("society diagnostics already exist")
        diag.mkdir()
        parity = []
        for row in records:
            if row["publication_status"] != "published":
                continue
            slot = society / "builders" / row["author"] / f"round-{row['round']:02d}"
            artifact = json.loads((society / "registry" / f"{row['id']}.json").read_text())
            original = json.loads((slot / "service/result.json").read_text())
            plain = judge(
                slot / "judge-view",
                artifact,
                diag / "plain" / row["id"],
                manifest["image"],
                seed=seed,
                round_=row["round"],
                instrument=False,
            )
            parity.append(dict(id=row["id"], equal=plain["families"] == original["families"]))
        (dest / "instrumentation-parity.json").write_text(json.dumps(parity, indent=2))
        # Predeclared deterministic eligibility/order/cap: observed correct cross-author edges,
        # earliest round then publication ID then edge. Selection is not based on intervention outcome.
        candidates = []
        for row in sorted(records, key=lambda r: (r["round"], r.get("id", ""))):
            for edge in sorted(row.get("cross_author_edges", [])):
                if is_cross(edge):
                    candidates.append((row, edge))
        interventions = []
        for row, edge in candidates[: args.edge_limit]:
            slot = society / "builders" / row["author"] / f"round-{row['round']:02d}"
            artifact = json.loads((society / "registry" / f"{row['id']}.json").read_text())
            original = json.loads((slot / "service/result.json").read_text())
            changed = judge(
                slot / "judge-view",
                artifact,
                diag / "intervention" / f"edge-{len(interventions):03d}",
                manifest["image"],
                seed=seed,
                round_=row["round"],
                ablate_edge=edge,
            )
            # Require a previously correct case that actually hit this edge, returned normally,
            # and lost correctness. A crash or mere edge hit is not functional evidence.
            witnesses = []
            old = {(d["family"], d["index"]): d for d in original["details"]}
            for item in changed["details"]:
                prior = old[(item["family"], item["index"])]
                if (
                    prior["correct"]
                    and edge in prior["executed_edges"]
                    and not item["error"]
                    and not item["input_mutated"]
                    and not item["correct"]
                ):
                    witnesses.append(dict(family=item["family"], index=item["index"]))
            hit = changed["edges"].get(edge, {}).get("mutated", 0) > 0
            interventions.append(
                dict(
                    id=row["id"],
                    edge=edge,
                    mutated=hit,
                    noncrashing_correctness_loss=bool(witnesses and hit),
                    witnesses=witnesses,
                    baseline=original["families"],
                    intervention=changed["families"],
                )
            )
        (dest / "interventions.json").write_text(json.dumps(interventions, indent=2))
        diagnostics.append(
            dict(
                seed=seed,
                condition=condition,
                parity_all_equal=all(p["equal"] for p in parity),
                replayed_publications=len(parity),
                eligible_edges=len(candidates),
                intervened_edges=len(interventions),
                confirmed_functional_edges=sum(x["noncrashing_correctness_loss"] for x in interventions),
                unique_intervened_edges=len({x["edge"] for x in interventions}),
                unique_confirmed_functional_edges=len(
                    {x["edge"] for x in interventions if x["noncrashing_correctness_loss"]}
                ),
            )
        )
        print(json.dumps(diagnostics[-1]), flush=True)
    with (args.output / "results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    (args.output / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2))
    accounting = usage_accounting(manifest, table)
    (args.output / "usage.json").write_text(json.dumps(accounting["all_attempt_usage"], indent=2))
    (args.output / "usage-accounting.json").write_text(json.dumps(accounting, indent=2))
    print(json.dumps(dict(societies=len(table), **accounting)), flush=True)


if __name__ == "__main__":
    main()
