"""Write manuscript tables from the existing analysis CSVs; never execute tools."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

NAMES = {
    "local-neutral": r"\neutralname",
    "local-boids": r"\boidsname",
    "independent": r"\independentname",
}
FAMILIES = ("clean", "revenue", "group", "monthly", "lookup", "window")


def tabular(columns, header, rows):
    return "\n".join(
        [r"\begin{tabular}{" + columns + "}", r"\toprule", header + r" \\", r"\midrule"]
        + [" & ".join(map(str, row)) + r" \\" for row in rows]
        + [r"\bottomrule", r"\end{tabular}", ""]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cells = list(csv.DictReader((args.analysis / "societies.csv").open()))
    if len(cells) != 9 or len({(c["seed"], c["condition"]) for c in cells}) != 9:
        raise ValueError("expected nine unique society cells")
    main_rows, cost_rows, mechanism_rows = [], [], []
    for c in cells:
        identity = [c["seed"], NAMES[c["condition"]]]
        adoption = f"{c['adoption_publications']}/{c['post_round_one_publications']}"
        rate = f"{float(c['post_round_one_adoption_rate']) * 100:.1f}\\%"
        main_rows.append(
            identity
            + [c["publications"], c["six_family_passes"], adoption, rate]
            + [
                c[k]
                for k in (
                    "correct_cross_author_cases",
                    "self_contained_six_authors",
                    "history_coverage_gap",
                    "physical_requests",
                )
            ]
        )
        cost_rows.append(
            identity
            + [f"{int(c[k]):,}" for k in ("input_tokens", "output_tokens", "cached_tokens")]
            + [c["physical_requests"], c["timeout_seconds"], c["generation_code_revision"][:7]]
        )
        mechanism_rows.append(
            identity
            + [
                f"{c['correct_cases']}/{c['declared_cases']}",
                f"{float(c['conditional_case_accuracy']) * 100:.2f}\\%",
            ]
            + [
                c[k]
                for k in (
                    "foreign_closure_publications",
                    "all_checks_import_or_simple_delegate_publications",
                    "root_ast_median",
                    "author_execution_pairs",
                    "first_fresh_collective_six_round",
                    "first_fresh_self_contained_six_round",
                )
            ]
        )
    tables = {
        "all-societies": (
            "rlrrrrrrrr",
            "Seed & Condition & Pubs & All-six & Adoption & Rate & Cross cases & Own-six & Gain & Calls",
            main_rows,
        ),
        "cost-provenance": (
            "rlrrrrrl",
            "Seed & Condition & Input tokens & Output tokens & Cached input & Calls & Wait (s) & Revision",
            cost_rows,
        ),
        "mechanism-details": (
            "rlrrrrrrrr",
            "Seed & Condition & Correct / declared & Accuracy & Foreign & Aliases & AST med. & Pairs & Group 6 & Own 6",
            mechanism_rows,
        ),
    }
    service = defaultdict(lambda: [0, 0])
    for row in csv.DictReader((args.analysis / "services.csv").open()):
        key = (row["family"], row["condition"])
        service[key][0] += int(row["passed"])
        service[key][1] += int(row["cases"])
    service_rows = []
    for family in FAMILIES:
        values = [family]
        for condition in NAMES:
            passed, total = service[family, condition]
            values.append(f"{passed}/{total} ({100 * passed / total:.2f})")
        service_rows.append(values)
    tables["service-reliability"] = (
        "lrrr",
        r"Service & \textcolor{NeutralBlue}{Neutral} & \textcolor{BoidsOrange}{Boids} & \textcolor{IndependentGray}{Independent}",
        service_rows,
    )
    for name, (columns, header, rows) in tables.items():
        (args.output / f"{name}.tex").write_text(tabular(columns, header, rows))
    print(f"wrote {len(tables)} tables from nine existing societies")


if __name__ == "__main__":
    main()
