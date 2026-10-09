# Manuscript revision 03 — presentation and source verification only

This revision implements the user’s **8-page body + references, no appendix** requirement. It retains all nine societies, all 432 opportunities, all 72 author profiles and the important tables in the English body. Seven figure sets replace redundant separate views; conceptual diagrams use Klein blue and condition colors remain unchanged. The Chinese report’s conceptual diagrams are synchronized.

No experiment, model call, grader call, generated-tool execution, new intervention or repair was performed. Numerical data are read from `../analysis-02`; its 461 input hashes still match `../collection-01`. The historical report and study remain unchanged. This revision does not create new statistical replicates or alter previous scores.

The previous `analysis-02/ANALYSIS_COMPLETE.json` and publication QA describe its manuscript exports at `56d04508db5784d9ae0d9d1e64109e5702de2fdd`. They remain historical; `publication-qa.json` and `REVISION_MANIFEST.json` here describe this revision’s current exports. Original full figure views remain available in `analysis-02` even where the paper now uses a combined atlas.

- `figures/`: 7 × editable SVG / vector PDF / 300-dpi PNG, with source hashes and claim/limitation contracts.
- `publication-qa.json`: final pages, references, source invariance, reproducible tables, artifact checks and visual review.
- `REVISION_MANIFEST.json`: exact artifact hashes, baseline revision and zero-experiment accounting.
- `paper/tool-ecology/CITATION_AUDIT.md` at repository root: checked scope and primary evidence for all 27 cited works; machine-readable companion includes bylines/years and disagreements.

Regeneration uses `studies/tool_ecology/scripts/refine_paper_figures.py` on existing CSVs only. Figure output requires a fresh directory. The supplied AAMAS class and bibliography style are preserved; no layout-font/margin workaround is used.
