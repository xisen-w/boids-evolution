# Tabular service adapters

Public functions are `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each returns a new list of dictionaries; input objects are not mutated. Only lookup uses `lookup_rows`.

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Regions are stripped and lowercased in normalized outputs. Missing units use `request['fill']` (`zero`, `mean`, or `median`); all-missing becomes zero and even-sized median averages its middle pair. Revenue is units times price, or `None` when either operand is missing. Group and monthly drop missing grouping keys and aggregate nonmissing revenue (`sum`, `mean`, `count`); monthly uses the first seven date characters. Lookup adds per-target revenue using exact normalized region matches, returning `None` for unknown region, missing/zero target, or missing revenue; it does not append target/manager. Window adds trailing ROWS mean over nonmissing revenues, including current row, with width `request['window']` (2/3/4). Group results sort by stringified keys. The APIs expect the specified input schema and do not validate malformed records.
