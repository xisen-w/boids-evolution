# Tool-ecology manuscript: completed exploratory study

This AAMAS-format working draft replaces the earlier pilot-centered narrative with
the completed nine-society native-tool study. It is not submitted and claims no
new benchmark victory. The supplied official AAMAS class and bibliography style
are retained with their notices. Author names are retained in source and hidden
by the anonymous class. No affiliations are invented.

All quantitative tables come from `studies/tool_ecology/evidence/v031/analysis-02`.
That analysis only reads the immutable `collection-01` public archive. It makes
zero model and grader calls and executes no generated programs. The preceding
paper, original pilot evidence and invalidated attempts remain preserved.

Figures share neutral blue `#2878B5`, Boids orange `#D97932`, independent gray
`#737C86`, Arial plot typography, seed marker shapes and explicit denominators.
Editable SVG, PDF, PNG, source CSV and figure contracts are in `analysis-02`.

Build this multi-file document with the installed TeX environment:

```sh
python studies/tool_ecology/scripts/write_analysis_tables.py \
  studies/tool_ecology/evidence/v031/analysis-02 --output paper/tool-ecology/tables
cd paper/tool-ecology
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

`main.pdf` is the reviewed export. The large source-derived tables disclose all
seeds, publication-level adoption, declared-case reliability, per-cell resource
use and original/recovery generation revisions. Supplements contain all nine
author networks and all 432 publication opportunities.

The related-work review is retained and condensed from the preceding authored
draft. The revision changes the current protocol, results and interpretation,
without presenting the earlier Wang/Zhang substrate as independent prior work.

Build note: the supplied AAMAS class under the local TeX Live 2025 environment
emits an end-of-document incomplete-conditional warning, also reproduced with a
minimal `Hello` document using that class. The class is preserved unmodified.
Both manuscript builds complete successfully; citations resolve, no overfull
boxes or missing glyphs are reported, and all exported pages were visually
reviewed. This is a working draft, not a claim of submission-ready page length.
