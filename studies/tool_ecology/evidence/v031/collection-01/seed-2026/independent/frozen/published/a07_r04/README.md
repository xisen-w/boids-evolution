# Native table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each accepts `(rows, lookup, request)` and returns new dictionaries without modifying inputs. Row services preserve column insertion order and append derived columns.

`request` requires `fill` (`zero`, `mean`, or `median`). Group/monthly additionally require `agg` (`sum`, `mean`, `count`); window requires `window` (2, 3, or 4). Example:

```python
from candidate import revenue, group
rows = [dict(id=1, region=' West ', product='x', date='2024-03-10', units=None, price_cents=20, cost_cents=2)]
req = {'fill':'zero', 'agg':'sum'}
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region':'west', 'sum_revenue_cents':0}]
```

Missing units are filled from nonmissing values; even medians average the middle pair and all-missing inputs fill with zero. `clean`, `group`, `monthly`, and `lookup` normalize nonmissing region strings by stripping/lowercasing; `revenue` and `window` preserve region values. Revenue is units times price, or `None` if either is missing. Grouping drops missing keys and ignores missing revenues; sum/count on empty revenue values are zero and mean is `None`. Lookup uses exact normalized region matching; unknown region, missing/zero target, or missing revenue yields `None`. Rolling means use the trailing rows including current, ignoring missing revenues without extending the window. Invalid fill/aggregation options raise `ValueError`.
