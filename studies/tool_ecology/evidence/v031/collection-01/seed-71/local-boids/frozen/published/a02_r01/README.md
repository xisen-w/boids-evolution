# Tabular service adapters

Native Python package, no dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. They implement the respective recurring service contracts; `lookup` (the function) uses the supplied lookup-row list. Inputs are not modified. The first two arguments are accepted by every adapter; irrelevant lookup data is ignored.

Example:
```python
from candidate import group
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-02', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [{'region': 'west', 'sum_revenue_cents': 100}]
```

`fill` supports zero/mean/median (all missing becomes zero); aggregations support sum/mean/count. Window widths are expected to be valid positive integers (the service contract specifies 2, 3, or 4). Rows are dictionaries with the documented service fields. Group/monthly omit missing grouping keys. Existing derived-key names, if supplied by callers, are overwritten.
