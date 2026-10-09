# Row-table services (a01_r03)

This package republishes the verified pure-Python service API from `a01_r02` as six root-level callables. Each function accepts `(rows, lookup, request)` and returns new row dictionaries; input rows, lookup data, and request are not mutated.

- `clean`: fill missing units (`fill`: `zero`, `mean`, or `median`; default `zero`, all missing -> 0), and strip/lowercase regions.
- `revenue`: fill units and append `revenue_cents` (`None` when units or price is missing).
- `group`: normalize regions, derive revenue, and group nonmissing regions using `agg` (`sum`, `mean`, `count`; default `sum`).
- `monthly`: as above, grouping by `date[:7]` and region, dropping missing keys.
- `lookup`: normalize row and lookup regions and append `revenue_cents_per_target`; unknown, absent/zero target, or missing revenue yields `None`.
- `window`: derive revenue and append the mean of nonmissing revenues in the trailing `window` rows including current (2, 3, or 4; default 2).

Original columns and row order are retained by row-returning services. Group outputs are sorted by stringified keys. Empty aggregation means are `None`; empty sums/counts are zero. Unsupported fill, aggregation, and window values raise `ValueError`.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

Implementation is imported from the declared dependency `published.a01_r02`; no additional third-party dependencies are required.
