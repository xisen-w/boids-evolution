"""Posthoc description of archived data. No generated code, grader or model executes.

The input collection is immutable. This script reads only sanitized public records,
frozen source/metadata, prior common-panel scores, graphs and usage summaries.
"""

import argparse
import ast
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ARMS = ("local-neutral", "local-boids", "independent")
SEEDS = (71, 108, 2026)
FAMILIES = ("clean", "revenue", "group", "monthly", "lookup", "window")
AUTHORS = tuple(f"a{i:02d}" for i in range(8))


def dependency_closure(identity, catalogue, active=None):
    """Return declared version closure; reject missing nodes and cycles."""
    active = set() if active is None else active
    if identity in active:
        raise ValueError(f"dependency cycle: {identity}")
    if identity not in catalogue:
        raise ValueError(f"missing dependency: {identity}")
    result = {identity}
    for dep in catalogue[identity]["dependencies"]:
        if catalogue[dep]["round"] >= catalogue[identity]["round"]:
            raise ValueError("dependency must precede publication")
        result |= dependency_closure(dep, catalogue, active | {identity})
    return result


def check_aliases(source, checks):
    """Conservative syntax labels, not functional attribution or originality."""
    tree = ast.parse(source)
    imports, functions = {}, {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("published."):
            for alias in node.names:
                imports[alias.asname or alias.name] = (node.module, alias.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            imports.pop(node.name, None)
            functions[node.name] = node
        if isinstance(node, ast.ClassDef):
            imports.pop(node.name, None)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for item in ast.walk(target):
                    if isinstance(item, ast.Name):
                        imports.pop(item.id, None)
    direct, delegates = [], []
    for family, name in checks.items():
        if name in imports:
            direct.append(family)
        if name in functions:
            body = functions[name].body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                body = body[1:]
            if len(body) == 1 and isinstance(body[0], ast.Return):
                call = body[0].value
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in imports:
                    delegates.append(family)
    return direct, delegates


def csv_write(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier analysis; choose a new output directory")
    root = args.collection
    used = {}

    def read(path):
        blob = path.read_bytes()
        used[str(path.relative_to(root))] = hashlib.sha256(blob).hexdigest()
        return blob.decode()

    def load(path):
        return json.loads(read(path))

    primary = list(csv.DictReader(read(root / "results.csv").splitlines()))
    primary = {(int(r["seed"]), r["condition"]): r for r in primary}
    common = {(r["seed"], r["condition"]): r for r in load(root / "fresh-panel/summary.json")}
    nonempty = {(r["seed"], r["condition"]): r for r in load(root / "request-execution-audit.json")["rows"]}
    final = load(root / "final-summary.json")
    differences = load(root / "output-differences.json")
    cells, turns, publications, authors, services, links = [], [], [], [], [], []
    for seed in SEEDS:
        for arm in ARMS:
            cell = root / f"seed-{seed}" / arm
            records = load(cell / "records.json")
            catalogue = {r["id"]: r for r in load(cell / "frozen/catalogue.json")}
            fresh = {
                r["id"]: r
                for r in load(root / "fresh-panel" / f"seed-{seed}" / arm / "publication-results.json")
            }
            graph = load(root / "execution-graphs" / f"seed-{seed}" / arm / "graph.json")
            base = primary[(seed, arm)]
            own = {}
            by_id = {}
            for row in records:
                if row["publication_status"] != "published":
                    continue
                identity = row["id"]
                cat = catalogue[identity]
                closure = dependency_closure(identity, catalogue)
                closure_authors = {catalogue[d]["author"] for d in closure}
                own[identity] = closure_authors == {row["author"]}
                source = read(cell / "frozen/published" / identity / "__init__.py")
                direct, delegates = check_aliases(source, cat["checks"])
                passed = sum(v["passed"] for v in row["service_counts"].values())
                total = sum(v["total"] for v in row["service_counts"].values())
                pub = dict(
                    seed=seed,
                    condition=arm,
                    id=identity,
                    author=row["author"],
                    round=row["round"],
                    declared_families=len(cat["checks"]),
                    original_passing_families=len(row["verified_families"]),
                    fresh_passing_families=len(fresh[identity]["passing_families"]),
                    self_contained_declared_closure=own[identity],
                    closure_versions=len(closure),
                    closure_authors=len(closure_authors),
                    oldest_dependency_round=min(catalogue[d]["round"] for d in closure),
                    root_ast_nodes=cat["ast_nodes"],
                    direct_import_adapter_families=len(direct),
                    simple_delegate_families=len(delegates),
                    all_checks_direct_imports=len(direct) == len(cat["checks"]),
                    all_checks_import_or_simple_delegate=len(direct) + len(delegates) == len(cat["checks"]),
                    original_correct_cases=passed,
                    original_declared_cases=total,
                    correct_cross_author_cases=row["correct_cross_author_requests"],
                    adoption_observed=row["correct_cross_author_requests"] > 0,
                )
                publications.append(pub)
                by_id[identity] = pub
            assert len(records) == 48 and len(fresh) == len(catalogue) == int(base["publications"])
            for rnd in range(1, 7):
                available = [
                    r for r in records if r["round"] <= rnd and r["publication_status"] == "published"
                ]
                current = [r for r in records if r["round"] == rnd]
                hist, selfhist, latest = defaultdict(set), defaultdict(set), {}
                for row in available:
                    identity, author = row["id"], row["author"]
                    families = set(fresh[identity]["passing_families"])
                    hist[author] |= families
                    if own[identity]:
                        selfhist[author] |= families
                    if author not in latest or row["round"] > latest[author]["round"]:
                        latest[author] = row
                collective = set().union(*hist.values()) if hist else set()
                selfbest = max((len(v) for v in selfhist.values()), default=0)
                latest_profiles = [set(fresh[r["id"]]["passing_families"]) for r in latest.values()]
                latest_collective = set().union(*latest_profiles) if latest_profiles else set()
                latest_selfbest = max(
                    (len(fresh[r["id"]]["passing_families"]) for r in latest.values() if own[r["id"]]),
                    default=0,
                )
                admitted = [r for r in current if r["publication_status"] == "published"]
                correct = sum(r.get("correct_service_requests", 0) for r in current)
                declared = sum(r.get("total_service_requests", 0) for r in current)
                turns.append(
                    dict(
                        seed=seed,
                        condition=arm,
                        round=rnd,
                        opportunities=8,
                        publications=len(admitted),
                        skips=sum(r["publication_status"] == "skip" for r in current),
                        rejected=sum(
                            r["publication_status"] == "publication_contract_failure" for r in current
                        ),
                        adoption_publications=sum(
                            r.get("correct_cross_author_requests", 0) > 0 for r in current
                        ),
                        correct_cross_author_cases=sum(
                            r.get("correct_cross_author_requests", 0) for r in current
                        ),
                        correct_cases=correct,
                        declared_cases=declared,
                        conditional_case_accuracy=correct / declared if declared else None,
                        six_service_declarations=sum(len(r.get("service_counts", {})) == 6 for r in admitted),
                        six_family_passes=sum(len(r["verified_families"]) == 6 for r in admitted),
                        fresh_history_collective_coverage=len(collective),
                        fresh_history_best_self_contained=selfbest,
                        fresh_history_coverage_gap=len(collective) - selfbest,
                        fresh_history_self_contained_six_authors=sum(len(selfhist[a]) == 6 for a in AUTHORS),
                        fresh_latest_collective_coverage=len(latest_collective),
                        fresh_latest_best_self_contained=latest_selfbest,
                        fresh_latest_coverage_gap=len(latest_collective) - latest_selfbest,
                    )
                )
            author_edges = {(e["provider"].split("_")[0], e["caller"].split("_")[0]) for e in graph["edges"]}
            for provider, caller in sorted(author_edges):
                links.append(dict(seed=seed, condition=arm, provider=provider, caller=caller))
            for a in AUTHORS:
                pubs = [
                    r
                    for r in publications
                    if r["seed"] == seed and r["condition"] == arm and r["author"] == a
                ]
                authors.append(
                    dict(
                        seed=seed,
                        condition=arm,
                        author=a,
                        publications=len(pubs),
                        adoption_publications=sum(r["adoption_observed"] for r in pubs),
                        self_contained_publications=sum(r["self_contained_declared_closure"] for r in pubs),
                        fresh_served_history_families=len(common[(seed, arm)]["author_profiles"][a]),
                        fresh_self_contained_history_families=len(
                            common[(seed, arm)]["self_contained_author_profiles"].get(a, [])
                        ),
                        served_other_authors=len({b for x, b in author_edges if x == a}),
                        used_other_authors=len({b for b, x in author_edges if x == a}),
                    )
                )
            for family in FAMILIES:
                offered = [
                    r["service_counts"][family] for r in records if family in r.get("service_counts", {})
                ]
                services.append(
                    dict(
                        seed=seed,
                        condition=arm,
                        family=family,
                        declarations=len(offered),
                        cases=sum(r["total"] for r in offered),
                        passed=sum(r["passed"] for r in offered),
                        fully_passing_publications=sum(r["passed"] == r["total"] for r in offered),
                    )
                )
            pubs = list(by_id.values())
            cellturns = [r for r in turns if r["seed"] == seed and r["condition"] == arm]
            postpubs = [r for r in pubs if r["round"] > 1]
            static_counts = Counter(r["all_checks_direct_imports"] for r in pubs)
            c = dict(
                seed=seed,
                condition=arm,
                publications=len(pubs),
                opportunities=48,
                six_family_passes=int(base["complete_six_publications"]),
                single_family_declarations=sum(r["declared_families"] == 1 for r in pubs),
                adoption_publications=sum(r["adoption_observed"] for r in pubs),
                post_round_one_publications=len(postpubs),
                post_round_one_adoption_rate=sum(r["adoption_observed"] for r in postpubs) / len(postpubs),
                adoption_authors=sum(
                    any(r["adoption_observed"] for r in pubs if r["author"] == a) for a in AUTHORS
                ),
                correct_cross_author_cases=int(base["correct_cross_author_requests"]),
                nonempty_correct_cross_author_cases=nonempty[(seed, arm)][
                    "nonempty_correct_cross_author_requests"
                ],
                correct_cases=int(base["correct_service_requests"]),
                declared_cases=int(base["total_declared_service_requests"]),
                conditional_case_accuracy=int(base["correct_service_requests"])
                / int(base["total_declared_service_requests"]),
                self_contained_six_authors=sum(
                    len(v) == 6 for v in common[(seed, arm)]["self_contained_author_profiles"].values()
                ),
                history_collective_coverage=common[(seed, arm)]["fresh_verified_family_coverage"],
                history_best_self_contained=common[(seed, arm)]["best_self_contained_author_coverage"],
                history_coverage_gap=common[(seed, arm)]["collective_minus_best_self_contained_coverage"],
                max_author_removal_loss=max(common[(seed, arm)]["coverage_loss"].values()),
                sustained_single_family_proxy=int(base["sustained_specialists"]),
                all_checks_direct_import_publications=static_counts[True],
                all_checks_import_or_simple_delegate_publications=sum(
                    r["all_checks_import_or_simple_delegate"] for r in pubs
                ),
                foreign_closure_publications=sum(not r["self_contained_declared_closure"] for r in pubs),
                foreign_closure_adoption_publications=sum(
                    not r["self_contained_declared_closure"] and r["adoption_observed"] for r in pubs
                ),
                root_ast_median=statistics.median(r["root_ast_nodes"] for r in pubs),
                author_execution_pairs=len(author_edges),
                first_fresh_collective_six_round=next(
                    r["round"] for r in cellturns if r["fresh_history_collective_coverage"] == 6
                ),
                first_fresh_self_contained_six_round=next(
                    r["round"] for r in cellturns if r["fresh_history_best_self_contained"] == 6
                ),
                final_latest_collective_coverage=cellturns[-1]["fresh_latest_collective_coverage"],
                final_latest_best_self_contained=cellturns[-1]["fresh_latest_best_self_contained"],
                final_latest_coverage_gap=cellturns[-1]["fresh_latest_coverage_gap"],
                physical_requests=int(base["physical_requests"]),
                input_tokens=int(base["input_tokens"]),
                output_tokens=int(base["output_tokens"]),
                cached_tokens=int(base["cached_tokens"]),
                generation_code_revision=base["generation_code_revision"],
                timeout_seconds=int(base["timeout_seconds"]),
            )
            assert c["adoption_publications"] == int(base["correct_cross_author_publications"])
            assert sum(r["original_correct_cases"] for r in pubs) == c["correct_cases"]
            assert sum(r["original_declared_cases"] for r in pubs) == c["declared_cases"]
            cells.append(c)
    assert len(publications) == 420 and len(turns) == 54 and len(authors) == 72
    aggregates = {}
    for arm in ARMS:
        rows = [r for r in cells if r["condition"] == arm]
        apubs = [r for r in publications if r["condition"] == arm]
        total_keys = [
            "publications",
            "adoption_publications",
            "post_round_one_publications",
            "correct_cross_author_cases",
            "nonempty_correct_cross_author_cases",
            "physical_requests",
            "input_tokens",
            "output_tokens",
            "cached_tokens",
            "correct_cases",
            "declared_cases",
            "all_checks_direct_import_publications",
            "all_checks_import_or_simple_delegate_publications",
            "foreign_closure_publications",
        ]
        sums = {k: sum(r[k] for r in rows) for k in total_keys}
        aggregates[arm] = dict(
            **sums,
            post_round_one_adoption_rate=sums["adoption_publications"] / sums["post_round_one_publications"],
            adoption_per_post_round_one_opportunity=sums["adoption_publications"] / 120,
            conditional_case_accuracy=sums["correct_cases"] / sums["declared_cases"],
            self_contained_six_authors=sum(r["self_contained_six_authors"] for r in rows),
            root_ast_median=statistics.median(r["root_ast_nodes"] for r in apubs),
            all_checks_import_or_simple_delegate_adoption_publications=sum(
                r["all_checks_import_or_simple_delegate"] and r["adoption_observed"] for r in apubs
            ),
        )
        expected = final["condition_aggregate"][arm]
        assert sums["physical_requests"] == expected["physical_requests"]
        assert sums["correct_cross_author_cases"] == expected["correct_cross_author_requests"]
    comparisons = []
    for seed in SEEDS:
        b = next(r for r in cells if r["seed"] == seed and r["condition"] == "local-boids")
        n = next(r for r in cells if r["seed"] == seed and r["condition"] == "local-neutral")
        comparisons.append(
            dict(
                seed=seed,
                adoption_publication_difference=b["adoption_publications"] - n["adoption_publications"],
                case_adoption_ratio=b["correct_cross_author_cases"] / n["correct_cross_author_cases"],
                conditional_accuracy_difference_pp=100
                * (b["conditional_case_accuracy"] - n["conditional_case_accuracy"]),
                input_token_ratio=b["input_tokens"] / n["input_tokens"],
                output_token_ratio=b["output_tokens"] / n["output_tokens"],
                physical_request_difference=b["physical_requests"] - n["physical_requests"],
                self_contained_six_author_difference=b["self_contained_six_authors"]
                - n["self_contained_six_authors"],
            )
        )
    summary = dict(
        classification="posthoc_descriptive_analysis_of_existing_public_records",
        model_calls=0,
        grader_calls=0,
        replicates="three societies per condition; matched workload/topology seeds, stochastic remote generation",
        condition_aggregates=aggregates,
        boids_minus_neutral_by_seed=comparisons,
        failed_cases=sum(r["declared_cases"] - r["correct_cases"] for r in cells),
        failed_field_sets=dict(Counter({})),
        original_collection_summary_unchanged=final,
        limitations=[
            "No case-level significance or causal mediation claims",
            "Posthoc metrics are explicitly descriptive",
            "Declared closure ownership does not imply originality",
            "Static syntax classifications do not establish dynamic necessity",
            "Latest-version and historical-library coverage answer different questions",
            "No new model calls, executions, probes, repairs or rescoring",
        ],
    )
    fields = Counter()
    for row in differences["results"]:
        for item in row["differing_field_sets"]:
            fields[" + ".join(item["fields"])] += item["failed_cases"]
    summary["failed_field_sets"] = dict(fields)
    args.output.mkdir(parents=True)
    for name, rows in [
        ("societies", cells),
        ("rounds", turns),
        ("publications", publications),
        ("authors", authors),
        ("services", services),
        ("author-links", links),
        ("seed-contrasts", comparisons),
    ]:
        csv_write(args.output / f"{name}.csv", rows)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.output / "input-manifest.json").write_text(
        json.dumps(
            dict(
                source_collection="../collection-01",
                files=used,
                analysis_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                model_calls=0,
                grader_calls=0,
                generated_code_executed=False,
            ),
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            dict(
                societies=len(cells),
                publications=len(publications),
                author_profiles=len(authors),
                rounds=len(turns),
                aggregates=aggregates,
                comparisons=comparisons,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
