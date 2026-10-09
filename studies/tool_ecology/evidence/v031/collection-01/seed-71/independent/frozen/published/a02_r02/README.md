# Tabular service adapters

This package re-exports the tested native implementations from `a02_r01` through
stable root APIs: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
The first parameter is a list of row dictionaries; lookup tables are lists of
`{region, target, manager}` dictionaries. Results are new lists and inputs are
not mutated.

Requests use `fill` = `zero`, `mean`, or `median`; grouped services use `agg` =
`sum`, `mean`, or `count`; window uses `window` = 2, 3, or 4. Examples:

```python
from candidate import clean, monthly
clean(rows, [], {"fill": "median"})
monthly(rows, [], {"fill": "mean", "agg": "sum"})
```

Regions are stripped/lowercased where specified; fill handles all-missing units
as zero. Revenue is None if units or price is missing. Grouping drops missing
keys and excludes missing revenues; count counts revenues. Lookup uses exact
normalized region keys and avoids division by missing/zero targets. Window means
available revenues within trailing ROWS, including current. This package depends
on received package `a02_r01`; date and numeric inputs are assumed to follow the
stated service contract.
