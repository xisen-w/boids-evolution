"""Describe failed DEV outputs by fields, without inferring their cause."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from ecology import workload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier output audit")
    manifest = json.loads((args.run / "manifest.json").read_text())
    if (
        hashlib.sha256(Path(workload.__file__).read_bytes()).hexdigest()
        != manifest["source_hashes"]["workload.py"]
    ):
        raise ValueError("workload source differs from generation manifest")
    results = []
    for root in sorted(args.run.glob("seed-*/*")):
        if not (root / "records.json").exists():
            continue
        kinds, families, columns = Counter(), Counter(), Counter()
        for rec in json.loads((root / "records.json").read_text()):
            if rec["publication_status"] != "published":
                continue
            slot = root / "builders" / rec["author"] / f"round-{rec['round']:02d}" / "service"
            grade = json.loads((slot / "result.json").read_text())
            inputs = {
                (x["family"], x["index"]): x for x in json.loads((slot / "inputs.json").read_text())["cases"]
            }
            output_file = slot / "traces/outputs.json"
            output_items = json.loads(output_file.read_text()) if output_file.exists() else []
            outputs = {(x["family"], x["index"]): x for x in output_items}
            for case in grade["details"]:
                if case["correct"]:
                    continue
                key = (case["family"], case["index"])
                families[case["family"]] += 1
                if case["error"]:
                    kinds["error"] += 1
                    continue
                if case["input_mutated"]:
                    kinds["input_mutation"] += 1
                    continue
                inp = inputs[key]
                expected = workload.reference(case["family"], inp["rows"], inp["lookup"], inp["request"])
                got = outputs[key]["output"]
                if not isinstance(got, list) or len(got) != len(expected):
                    kinds["shape_or_row_count"] += 1
                    continue
                different = set()
                for actual, wanted in zip(got, expected):
                    if not isinstance(actual, dict):
                        different.add("<row_type>")
                        continue
                    different.update(set(actual) ^ set(wanted))
                    for name in actual.keys() & wanted.keys():
                        if not workload.equal([{name: actual[name]}], [{name: wanted[name]}]):
                            different.add(name)
                columns[tuple(sorted(different))] += 1
                kinds["value_or_keys"] += 1
        results.append(
            dict(
                society=str(root.relative_to(args.run)),
                frozen=(root / "frozen/freeze.json").exists(),
                failure_kinds=dict(kinds),
                failed_cases_by_family=dict(families),
                differing_field_sets=[
                    dict(fields=list(names), failed_cases=count) for names, count in columns.most_common()
                ],
            )
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            dict(
                classification="descriptive_original_DEV_output_differences",
                caveat="A field mismatch does not establish a code cause or rule effect; cases are not independent societies.",
                analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                model_calls=0,
                results=results,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
