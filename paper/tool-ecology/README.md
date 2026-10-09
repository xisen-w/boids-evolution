# Tool-ecology manuscript: eight-page body, no appendix

The current official-AAMAS-class export has **8 main-text pages plus 1 reference page (9 total), with no appendix**. This is an anonymous working draft, not a submission. The supplied class, bibliography style, fonts and margins are preserved; no manual font reduction, negative spacing or margin changes were used to fit the page limit. Author names remain in source and are hidden by the class; no affiliations are invented.

The body contains seven vector figures and four data tables: both refined workflows, all nine endpoints, all nine author networks, all 432 publication opportunities, all 72 own/served author histories, all seed trajectories, the original narrowing sequence, service reliability, resource usage and generation provenance. The atlas combines three former supplementary views; its original-round and common-panel columns are explicitly distinguished. The old appendix is removed, with evidence integrated into the body.

All quantitative data still come from `studies/tool_ecology/evidence/v031/analysis-02`, which reads immutable `collection-01`. The study is closed: this revision makes zero model/grader calls and executes no archived generated programs. No scores, failures or generation histories change.

The two concept diagrams use Klein blue `#002FA7`. Treatment colors remain neutral blue `#2878B5`, Boids orange `#D97932` and independent gray `#737C86`; conceptual blue does not denote a treatment. Editable SVG, PDF, PNG, source hashes and figure contracts are in `studies/tool_ecology/evidence/v031/manuscript-03/figures`. Original full analysis exports remain in `analysis-02`.

[CITATION_AUDIT.md](CITATION_AUDIT.md) records primary evidence, checked scope and corrections for all 27 cited works; [citation-audit.json](citation-audit.json) provides machine-readable details. Author/PDF metadata disagreements are disclosed. Related-work claims were narrowed where abstract-level support was insufficient. The authors’ own substrate is never presented as independent earlier Wang–Zhang work. The review makes no exhaustive or universal priority claim.

Build from the repository root using the configured Python plotting runtime and installed TeX:

```sh
python studies/tool_ecology/scripts/refine_paper_figures.py \
  studies/tool_ecology/evidence/v031/analysis-02 --output /tmp/boids-fresh-figures
python studies/tool_ecology/scripts/write_analysis_tables.py \
  studies/tool_ecology/evidence/v031/analysis-02 --output paper/tool-ecology/tables
cd paper/tool-ecology
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

Copy freshly generated figure PDFs into `paper/tool-ecology/figures` before building if reproducing figure edits. The reviewed PDF is [main.pdf](main.pdf). The revision QA and content hashes are in `studies/tool_ecology/evidence/v031/manuscript-03/publication-qa.json` and `REVISION_MANIFEST.json`. The earlier `analysis-02` completion marker describes its exports at commit `56d04508db5784d9ae0d9d1e64109e5702de2fdd`; it is preserved as historical evidence, not misrepresented as the hash list for this revised manuscript.

Build note: the supplied AAMAS class under local TeX Live 2025 emits an incomplete-conditional message (also reproduced by a minimal Hello document), a last-page balance warning, and a warning that the fully occupied atlas/trajectory page contains only floats. The upstream class is preserved unmodified. These do not indicate unresolved citations or overflow. Final PDF compilation, page-count checks and visual QA are recorded separately; no claim of conference submission is made.
