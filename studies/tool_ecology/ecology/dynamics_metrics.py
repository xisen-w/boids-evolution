"""Descriptive society-level metrics. Test cases are not independent societies."""

from collections import defaultdict


def summarize(rows):
    profiles = defaultdict(set)
    history = defaultdict(dict)
    cross = []
    for row in rows:
        verified = sorted(set(row.get("verified_families", [])))
        profiles[row["author"]].update(verified)
        history[row["author"]][row["round"]] = verified
        if verified and row.get("verified_cross_author_edges"):
            cross.append(row["id"])
    specialists = []
    for author in sorted(history):
        current, start, previous = None, None, None
        for round_, families in sorted(history[author].items()):
            family = families[0] if len(families) == 1 else None
            if family != current or previous is None or round_ != previous + 1:
                if current and previous - start + 1 >= 3:
                    specialists.append(
                        dict(author=author, family=current, start_round=start, end_round=previous)
                    )
                current, start = family, round_
            previous = round_
        if current and previous - start + 1 >= 3:
            specialists.append(dict(author=author, family=current, start_round=start, end_round=previous))
    coverage = sorted(set().union(*profiles.values())) if profiles else []
    counts = {family: sum(family in p for p in profiles.values()) for family in coverage}
    overlaps = []
    authors = sorted(profiles)
    for i, a in enumerate(authors):
        for b in authors[i + 1 :]:
            union = profiles[a] | profiles[b]
            if union:
                overlaps.append(len(profiles[a] & profiles[b]) / len(union))
    return dict(
        publications=sum(r.get("publication_status") == "published" for r in rows),
        verified_family_coverage=coverage,
        author_profiles={a: sorted(p) for a, p in sorted(profiles.items())},
        verified_authors_per_family=counts,
        redundant_author_family_pairs=sum(max(0, n - 1) for n in counts.values()),
        mean_author_profile_jaccard=sum(overlaps) / len(overlaps) if overlaps else None,
        sustained_specialists=specialists,
        correct_cross_author_publications=len(cross),
        correct_cross_author_requests=sum(r.get("correct_cross_author_requests", 0) for r in rows),
        correct_service_requests=sum(r.get("correct_service_requests", 0) for r in rows),
        total_service_requests=sum(r.get("total_service_requests", 0) for r in rows),
        publications_with_correct_cross_author_requests=sum(bool(r.get("cross_author_edges")) for r in rows),
        correct_cross_author_publication_ids=cross,
        correct_publications=sum(bool(r.get("verified_families")) for r in rows),
        observed_cross_author_edges=sorted({e for r in rows for e in r.get("cross_author_edges", [])}),
    )
