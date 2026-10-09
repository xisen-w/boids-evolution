# Descriptive analysis of the completed frozen collection

This directory contains only **posthoc analysis of existing public evidence**.
No new model calls, grader calls, generated-program execution, repairs or probes
are performed. The immutable source is `../collection-01`. None of its scores,
freezes, intervention selections, failed attempts or generation revisions change.

The Chinese analysis is `docs/tool-ecology/DEEP_ANALYSIS_ZH.md` and its PDF.
The complete English AAMAS-format working draft is `paper/tool-ecology/main.pdf`.
The original final report remains an unchanged historical completion record.

## Source data and interpretation

- `societies.csv`: all nine cells, adoption denominators, reliability, own-author
  histories, latest-version endpoint, alias syntax, root AST size, costs/revisions.
- `all-societies.md`: the large all-seed overview table.
- `rounds.csv`: all 54 society-rounds, original per-round cases and already scored
  common-panel historical/latest-version profiles. These panels are not conflated.
- `publications.csv`: all 420 admitted root packages, declarations, original/fresh
  breadth, declared closure ownership, conservative adapter syntax and root size.
- `authors.csv`: all 72 author histories and observed provider/caller participation.
- `services.csv`: every seed-condition-family numerator and denominator.
- `author-links.csv`: directed unique provider-to-caller author pairs, projected
  from archived correct-execution version pairs. Not the ring, not causal effects.
- `seed-contrasts.csv`: descriptive Boids-minus-neutral seed matches. Seeds match
  topology/data, not deterministic remote generation. No independence is claimed.
- `summary.json`: exact aggregates, contrasts and limitations, with the original
  collection summary retained. Input tokens already include cached input.
- `input-manifest.json`: exact SHA256 for all source files read and analysis source.
- `publication-qa.json`: reproducibility, table, source-hash and final PDF checks.
- `ANALYSIS_COMPLETE.json`: hashes of the published analysis/manuscript outputs,
  distinct from the original study's unchanged completion record.
- `figures/`: ten figures, each PNG, editable-text SVG and TrueType PDF. The
  figure contracts record claims, source tables, palette and inferential limits.

Adoption requires at least one correct original service case executing foreign
code. Main rates use admitted publications after round one; opportunity rates
include all 120 post-initial slots per condition. Cases, publications and authors
remain nested inside only three societies per condition. No case-level p-values
or confidence intervals are manufactured.

Own-author capability is a union of prior passing versions whose entire declared
closure belongs to the author. It does not establish original code, independent
understanding or absence of copying. Latest-version coverage is separately
reported as a sensitivity description, not a new execution or a paid baseline.

Imported-adapter and single-return-delegate labels are conservative AST syntax
checks on declared root adapters. They do not establish functional necessity,
originality, zero effort or absence of unrecognized wrapper patterns. Same-author
version reuse also qualifies syntactically; foreign ownership is a separate field.

Root AST size excludes dependency code and is neither total program size nor
computational complexity. Pooled medians do not replace the nine society medians.
Reliability is conditioned on admitted declared service cases, with every family
denominator retained. It is not a specialization score or an external TEST result.

## Main descriptive observations

Post-initial adoption is Boids57/115 versus neutral26/116; per all opportunities,
57/120 versus26/120. The three Boids cells have17/20/20 adopting publications and
15 adopting author histories in total; neutral4/9/13 and8 authors. Correct case
counts remain1932/936, nonempty1607/780. Every independent cell has zero foreign
adoption by construction; this is not proof of an emergent organization advantage.

Own-author six-family histories total13/24 Boids,20/24 neutral,24/24 independent.
All final common-panel history and latest-version coverage gaps are zero. The
only two positive earlier gaps are first-round, pre-exchange observations in
neutral71 and Boids2026. Both disappear in round two. They cannot be attributed
to tool exchange. This does not rule out other unmeasured collaboration benefits.

Among adopting packages, all checks are imported adapters or simple delegates in
39/57 Boids and19/26 neutral packages. These patterns support broad-library
transmission as an observable form of adoption, not necessary complementary roles.
Pooled root AST medians114/822.5/755 coexist with Boids34.3% more input tokens than
independent generation and nearly equal output tokens. Per-seed costs vary.

The original sustained single-family proxy stays zero; four narrow declarations
and the existing isolated writeback diagnosis remain visible. No corrected
program is counted as an observed persistent role. The original420 replay
parities and72 intervention records/70 unique edges/69 unique witnesses remain
unchanged. One empty-table edge remains unconfirmed.

## Reproduce without any API or grader

Use `boids-core-dev-runtime` for analysis/plots, and the installed TeX environment
for the authored documents. Choose a fresh output directory for the analyzer.

```sh
python studies/tool_ecology/scripts/analyze_frozen_collection.py \
  studies/tool_ecology/evidence/v031/collection-01 --output /tmp/boids-analysis-new
python studies/tool_ecology/scripts/plot_frozen_analysis.py \
  /tmp/boids-analysis-new --collection studies/tool_ecology/evidence/v031/collection-01
python studies/tool_ecology/scripts/render_analysis_report.py \
  docs/tool-ecology/DEEP_ANALYSIS_ZH.md --output /tmp/analysis-report.tex --repo .
python studies/tool_ecology/scripts/write_analysis_tables.py \
  /tmp/boids-analysis-new --output /tmp/boids-manuscript-tables
```

For the Chinese document, place generated TeX beside its Markdown or keep that
directory as the compilation working directory so relative figure paths resolve.
The English manuscript README gives its multi-file build command. Plot drawing,
preview generation and visual checks all use Python; no alternate R rendering.

This is a final analysis package, not a preregistration. The fixed paid study is
closed and its automated experiment follow-up remains paused.
