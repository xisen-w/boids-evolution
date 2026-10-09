# tabular_services

Native Python implementations of the six specified row-table services. Public adapters all take `(rows, lookup, request)` and return new lists/dicts without mutating inputs. Original columns and row order are retained for row-wise outputs.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None, 'price_cents': 10}]
clean(rows, [], {'fill': 'zero'})
revenue(rows, [], {'fill': 'zero'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'sum'})
lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 2})
```

Fill accepts `zero`, `mean`, or `median` (all-missing becomes zero); aggregation accepts `sum`, `mean`, or `count`; window accepts 2, 3, or 4 rows. Missing grouping keys are dropped. Lookup uses normalized region keys; its manager field is ignored. `lookup` here names the adapter, so use `from candidate import lookup`.
