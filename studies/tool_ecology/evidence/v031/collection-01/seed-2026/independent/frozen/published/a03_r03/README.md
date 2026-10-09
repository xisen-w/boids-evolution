# Tabular transformations

This package exposes six pure service adapters from the verified `a03_r02` native implementation. Import with `from candidate import clean, revenue, group, monthly, lookup, window` (or use the equivalent functions on the published package). Each takes `(rows, lookup, request)` and returns new row dictionaries without mutating inputs.

- `clean`: normalize region with strip/lower and fill missing units.
- `revenue`: fill units and append `revenue_cents`; region spelling is unchanged.
- `group`: normalize region, derive revenue, and aggregate by region.
- `monthly`: same, grouped by YYYY-MM month and region.
- `lookup`: normalize region, derive revenue, append revenue divided by exact-key lookup target (does not append lookup fields).
- `window`: derive revenue and append trailing ROWS mean, including current row.

Fill mode is `request['fill']`: `zero`, `mean`, or `median`; all-missing units fill with zero. Group aggregation uses `request['agg']`: `sum`, `mean`, or `count`. Window size uses `request['window']`: 2, 3, or 4. Grouping drops missing keys; aggregate mean of an empty set is None, while sum/count are zero. Missing revenue is excluded from aggregation and rolling means. Revenue is None if either operand is missing. Unknown/zero/missing lookup targets yield None. Invalid parameter values raise `ValueError`.

Example:

```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'units': 0, 'price_cents': 25, 'revenue_cents': 0}
]
```

This facade intentionally depends on `a03_r02`; it adds no independent algorithm or external dependency.
