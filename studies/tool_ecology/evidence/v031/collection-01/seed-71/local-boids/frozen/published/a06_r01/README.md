# tabular_services

Native Python adapters for six row-dictionary services. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list and does not mutate inputs. Region strings are stripped and lowercased. `request.fill` is `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. Aggregation uses `request.agg` (`sum`, `mean`, `count`; default `sum`). Window accepts 2, 3, or 4 (`request.window`).

Example:
```python
from candidate import revenue
rows = [{'region': ' WEST ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

`clean` preserves existing fields and order while normalizing region/filling units. The other row-wise services append `revenue_cents`; `lookup` additionally appends `revenue_cents_per_target`, and `window` appends `roll_revenue_cents`. Group outputs contain only grouping keys and the requested aggregate. Lookup matches normalized region keys (later duplicate lookup entries take precedence). Missing group keys are dropped; means of empty groups are `None`.
