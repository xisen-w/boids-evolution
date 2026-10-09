# tabular_services

Dependency-free implementations of all six service families. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`; each returns a new list of row dictionaries (or grouped output) and does not mutate its inputs. Rows are dictionaries. `request.fill` is `zero`, `mean`, or `median` (default `zero`); missing units use the selected statistic, with all-missing becoming zero. `request.agg` is `sum`, `mean`, or `count` (default `sum`). `request.window` is 2, 3, or 4.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {})[0]['revenue_cents'] == 100
assert group(rows, [], {}) == [{'region': 'west', 'sum_revenue_cents': 100}]
```

Region strings are stripped and lowercased. Grouping drops missing keys. Revenue is `None` when an operand is missing; means ignore missing revenue and are `None` for empty sets. `lookup` uses the normalized row region to match lookup region keys exactly; lookup keys themselves are not normalized. Only the fields specified by the service contracts are derived; no date validation is performed.
