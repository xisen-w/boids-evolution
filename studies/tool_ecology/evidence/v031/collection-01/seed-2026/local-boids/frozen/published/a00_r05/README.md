# Tabular service adapters

Exports `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`; each
has signature `(rows, lookup, request)` and returns a new list of dictionaries
without mutating inputs. The implementations are reused from the verified
`published.a04_r02` package.

- `clean`: strip/lower region strings and fill missing units.
- `revenue`: fill units and append `revenue_cents`.
- `group`: normalize regions and aggregate nonmissing revenues by region.
- `monthly`: aggregate by month (`date[:7]`) and normalized region.
- `lookup`: add revenue per exact normalized-region target; no target/manager
  columns are added.
- `window`: add mean revenue over trailing rows including current.

`request['fill']` is `zero`, `mean`, or `median` (default `zero`); all-missing
units fill to zero. Even medians average the central pair. Aggregate requests
use `request['agg']` = `sum`, `mean`, or `count` (default `sum`), excluding
missing revenues. Empty means are `None`; empty sums/counts are zero.
`request['window']` accepts 2, 3, or 4 (default 2). Lookup yields `None` for
unknown regions, missing/zero targets, or missing revenue. Output preserves
specified column/order behavior. Invalid parameter values raise `ValueError`.

Example:
```python
from candidate import revenue
revenue([{'region': 'West', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': 'West', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
