# Tabular row services

Pure Python adapters operate on lists of dictionaries and return fresh dictionaries; input rows, lookup data, and requests are not mutated. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.

`request` supports `fill` (`zero`, `mean`, `median`; default `zero`), `agg` (`sum`, `mean`, `count`; default `sum`), and `window` (2, 3, or 4; required by `window`). Missing units are filled using the selected statistic; all-missing units fill with zero and even medians average the central values. Region strings are stripped and lowercased. Revenue is `units * price_cents`, or `None` if either is missing. Grouping drops missing keys; sum/count of empty value sets are zero and mean is `None`. Lookup matches normalized row regions exactly against lookup region keys and returns `None` for absent/zero targets or missing revenue. Rolling means use trailing rows including current and ignore missing revenues.

```python
from candidate import clean, revenue, group
rows = [{'region': ' NORTH ', 'units': None, 'price_cents': 20, 'date': '2025-01-03'}]
request = {'fill': 'zero', 'agg': 'sum'}
assert clean(rows, [], request)[0]['region'] == 'north'
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'north', 'sum_revenue_cents': 0}]
```

Only the documented service fields/operations are provided; input schemas are expected to use the specified types.
