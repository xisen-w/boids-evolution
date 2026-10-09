"""Fresh common DEV-data panel and graph-derived author-removal diagnostic.

No inference. This is distinct from original scores, and is not sealed TEST
performance, agent adaptation, or a noncrashing function-return intervention.
"""

import argparse
import hashlib
import json
from pathlib import Path

from ecology.registry import Registry
from ecology.services import judge

PANEL_SEED = 31415926
PANEL_ROUND = 99


def structural_coverage(cards, passing):
    all_families = sorted({f for families in passing.values() for f in families})
    after = {}
    self_contained = {}
    for author in sorted({c["author"] for c in cards}):
        blocked = {c["id"] for c in cards if c["author"] == author}
        while True:
            extra = {c["id"] for c in cards if set(c["dependencies"]) & blocked}
            if extra <= blocked:
                break
            blocked |= extra
        after[author] = sorted(
            {f for identity, families in passing.items() if identity not in blocked for f in families}
        )
        # An adapter that serves a family via a neighbor is not independently
        # runnable author competence. Include own-history dependencies only if
        # their entire declared closure also belongs to this author.
        own = {c["id"] for c in cards if c["author"] == author}
        while True:
            invalid = {c["id"] for c in cards if c["id"] in own and set(c["dependencies"]) - own}
            if not invalid:
                break
            own -= invalid
        self_contained[author] = sorted({f for identity in own for f in passing.get(identity, [])})
    best_self = max(map(len, self_contained.values()), default=0)
    return dict(
        all_families=all_families,
        after_author_removal=after,
        coverage_loss={a: len(all_families) - len(fs) for a, fs in after.items()},
        self_contained_author_profiles=self_contained,
        best_self_contained_author_coverage=best_self,
        collective_minus_best_self_contained_coverage=len(all_families) - best_self,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier frozen audit")
    if not (args.run / "COMPLETE.json").exists():
        raise ValueError("batch must complete before this audit")
    manifest = json.loads((args.run / "manifest.json").read_text())
    args.output.mkdir(parents=True)
    results = []
    for root in sorted(args.run.glob("seed-*/*")):
        if not (root / "registry").exists():
            continue
        Registry.verify_freeze(root / "frozen")
        registry = Registry(root / "registry")
        frozen_cards = json.loads((root / "frozen/catalogue.json").read_text())
        if sorted(frozen_cards, key=lambda c: c["id"]) != [
            card for _, card in sorted(registry.artifacts.items())
        ]:
            raise ValueError("registry metadata differs from frozen catalogue")
        out = args.output / root.parent.name / root.name
        out.mkdir(parents=True)
        rows = []
        passing = {}
        for identity, card in sorted(registry.artifacts.items()):
            library = registry.materialize({identity}, out / identity / "view")
            grade = judge(
                library,
                card,
                out / identity / "grade",
                manifest["image"],
                seed=PANEL_SEED,
                round_=PANEL_ROUND,
                instrument=False,
            )
            good = sorted(f for f, s in grade["families"].items() if s["passed"] == s["total"])
            passing[identity] = good
            rows.append(
                dict(
                    id=identity,
                    author=card["author"],
                    publication_round=card["round"],
                    passing_families=good,
                    service_counts=grade["families"],
                )
            )
        graph = structural_coverage(list(registry.artifacts.values()), passing)
        profiles = {
            author: sorted({f for row in rows if row["author"] == author for f in row["passing_families"]})
            for author in sorted({r["author"] for r in rows})
        }
        result = dict(
            seed=int(root.parent.name.split("-")[1]),
            condition=root.name,
            panel_seed=PANEL_SEED,
            panel_round=PANEL_ROUND,
            evaluated_publications=len(rows),
            author_profiles=profiles,
            **graph,
            fresh_verified_family_coverage=len(graph["all_families"]),
            best_author_coverage=max(map(len, profiles.values()), default=0),
            complementarity_coverage_gap=len(graph["all_families"])
            - max(map(len, profiles.values()), default=0),
        )
        (out / "publication-results.json").write_text(json.dumps(rows, indent=2))
        (out / "summary.json").write_text(json.dumps(result, indent=2))
        results.append(result)
        print(json.dumps(result), flush=True)
    (args.output / "summary.json").write_text(json.dumps(results, indent=2))
    (args.output / "manifest.json").write_text(
        json.dumps(
            dict(
                classification="additional_frozen_DEV_robustness_diagnostic",
                generation_code_revision=manifest["code_revision"],
                analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                panel_seed=PANEL_SEED,
                panel_round=PANEL_ROUND,
                model_calls=0,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
