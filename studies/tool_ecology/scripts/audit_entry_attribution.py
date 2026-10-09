"""Regrade old frozen societies with corrected service-entry attribution.

Preserves the old feedback and scores. This is an infrastructure diagnostic,
not behavior under corrected feedback. Incomplete societies are inventoried
with their full API usage, but never passed off as completed societies.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from ecology.dynamics import is_cross, service_evidence
from ecology.dynamics_metrics import summarize
from ecology.registry import Registry, file_hashes
from ecology.services import judge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--edge-limit", type=int, default=6)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier attribution audit")
    if not any((args.run / n).exists() for n in ("COMPLETE.json", "INVALIDATED_MEASUREMENT.json")):
        raise ValueError("run must be complete or explicitly invalidated, with no active writer")
    args.output.mkdir(parents=True)
    manifest = json.loads((args.run / "manifest.json").read_text())
    ecology = Path(__file__).resolve().parents[1] / "ecology"
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    (args.output / "manifest.json").write_text(
        json.dumps(
            dict(
                classification="infrastructure_attribution_diagnostic_under_old_feedback",
                generation_manifest=manifest,
                analysis_revision=revision,
                analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                grader_source_hashes={k: v for k, v in file_hashes(ecology).items() if k.endswith(".py")},
                model_calls=0,
                edge_selection="first corrected foreign entry edges by round, publication ID, edge; capped per society",
                edge_limit=args.edge_limit,
            ),
            indent=2,
        )
    )
    inventory, summaries = [], []
    for root in sorted(args.run.glob("seed-*/*")):
        if not (root / "config.json").exists():
            continue
        usage = json.loads((root / "usage.json").read_text())
        frozen = (root / "frozen/freeze.json").exists()
        inventory.append(dict(society=str(root.relative_to(args.run)), frozen=frozen, **usage))
        if not frozen:
            continue
        Registry.verify_freeze(root / "frozen")
        records = json.loads((root / "records.json").read_text())
        registry = Registry(root / "registry")
        dest = args.output / root.parent.name / root.name
        dest.mkdir(parents=True)
        corrected, grades, parity = [], {}, []
        for row in records:
            fixed = dict(row)
            if row["publication_status"] == "published":
                slot = root / "builders" / row["author"] / f"round-{row['round']:02d}"
                result = judge(
                    slot / "judge-view",
                    registry.artifacts[row["id"]],
                    dest / "raw-grades" / row["id"],
                    manifest["image"],
                    seed=int(root.parent.name.split("-")[1]),
                    round_=row["round"],
                )
                original = json.loads((slot / "service/result.json").read_text())
                equal = result["families"] == original["families"]
                parity.append(dict(id=row["id"], equal=equal))
                if not equal:
                    raise RuntimeError(f"attribution repair changed service scores: {row['id']}")
                fixed.update(service_evidence(result))
                grades[row["id"]] = result
            corrected.append(fixed)
        candidates = []
        for row in sorted(corrected, key=lambda r: (r["round"], r.get("id", ""))):
            result = grades.get(row.get("id"))
            if result is None:
                continue
            for edge in sorted(row.get("cross_author_edges", [])):
                if result["edges"].get(edge, {}).get("service_entries", 0) and is_cross(edge):
                    candidates.append((row, edge))
        interventions = []
        for row, edge in candidates[: args.edge_limit]:
            slot = root / "builders" / row["author"] / f"round-{row['round']:02d}"
            changed = judge(
                slot / "judge-view",
                registry.artifacts[row["id"]],
                dest / "raw-interventions" / f"edge-{len(interventions):02d}",
                manifest["image"],
                seed=int(root.parent.name.split("-")[1]),
                round_=row["round"],
                ablate_edge=edge,
            )
            prior = {(d["family"], d["index"]): d for d in grades[row["id"]]["details"]}
            witnesses = [
                dict(family=d["family"], index=d["index"])
                for d in changed["details"]
                if prior[(d["family"], d["index"])]["correct"]
                and edge in prior[(d["family"], d["index"])]["executed_edges"]
                and not d["correct"]
                and not d["error"]
                and not d["input_mutated"]
            ]
            hit = changed["edges"].get(edge, {}).get("mutated", 0) > 0
            interventions.append(
                dict(
                    id=row["id"],
                    edge=edge,
                    mutated=hit,
                    noncrashing_correctness_loss=bool(hit and witnesses),
                    witnesses=witnesses,
                )
            )
        before, after = summarize(records), summarize(corrected)
        summary = dict(
            society=str(root.relative_to(args.run)),
            original_correct_cross_author_requests=before["correct_cross_author_requests"],
            corrected_correct_cross_author_requests=after["correct_cross_author_requests"],
            original_cross_author_publications=before["correct_cross_author_publications"],
            corrected_cross_author_publications=after["correct_cross_author_publications"],
            replayed_publications=len(parity),
            service_scores_all_equal=all(p["equal"] for p in parity),
            intervened_foreign_entry_edges=len(interventions),
            confirmed_noncrashing_edges=sum(i["noncrashing_correctness_loss"] for i in interventions),
        )
        for name, value in (
            ("original-feedback-records.json", records),
            ("corrected-records.json", corrected),
            ("summary.json", summary),
            ("score-parity.json", parity),
            ("interventions.json", interventions),
        ):
            (dest / name).write_text(json.dumps(value, indent=2))
        summaries.append(summary)
        print(json.dumps(summary), flush=True)
    (args.output / "summary.json").write_text(json.dumps(summaries, indent=2))
    (args.output / "inventory.json").write_text(json.dumps(inventory, indent=2))
    for name in ("ABORTED.json", "INVALIDATED_MEASUREMENT.json"):
        if (args.run / name).exists():
            shutil.copyfile(args.run / name, args.output / name)


if __name__ == "__main__":
    main()
