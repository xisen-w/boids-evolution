# Native tabular service utilities

The package exports six adapters, each with signature `family(rows, lookup, request)`:
`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. `rows` and `lookup`
are lists of mappings and `request` is a mapping. Outputs contain fresh row dictionaries;
inputs are not mutated.

- `clean`: normalize string regions with strip/lower; fill missing units, preserving columns and row order.
- `revenue`: fill missing units and append `revenue_cents`; region is not normalized.
- `group`: normalize region, derive revenue, and aggregate nonmissing revenue by nonmissing region.
- `monthly`: as group, by nonmissing (month, region); month is the first seven date characters.
- `lookup`: normalize row and lookup regions; add revenue divided by the matching target, or `None` for missing/zero target or missing revenue. Duplicate normalized keys use the last lookup row.
- `window`: derive revenue and append the trailing-row mean (including current row), excluding missing revenue values.

`request['fill']` is `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. `request['agg']` is `sum`, `mean`, or `count` (default `sum`); mean of an empty group is `None`, and sum/count of an empty value set are zero. `request['window']` is 2, 3, or 4 (default 2). Invalid options raise `ValueError`.

Example:
```python
from candidate import group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}
]
```
