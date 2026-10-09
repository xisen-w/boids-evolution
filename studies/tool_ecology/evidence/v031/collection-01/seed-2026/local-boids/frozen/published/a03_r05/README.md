# Row-table services

Public API: `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each accepts rows as a list of dictionaries, lookup data as dictionaries, and request as a dictionary; inputs are not mutated. Implementations are delegated to the verified `published.a07_r04` dependency.

`clean` normalizes region with strip/lower and fills missing units. Fill mode is `request['fill']`: zero, mean, or median (even median averages central values; all-missing becomes zero). `revenue` adds `revenue_cents` (null when units or price is null). `group` and `monthly` normalize regions, derive revenue, discard missing grouping keys, and aggregate nonmissing revenues with `request['agg']` (`sum`, `mean`, or `count`). Monthly keys use the first seven date characters; results are sorted by stringified keys. Empty sum/count are zero, empty mean is null. `lookup` appends `revenue_cents_per_target`, using exact normalized region keys; absent/unknown target, zero target, or null revenue produces null. `window` appends trailing ROWS mean `roll_revenue_cents`, including current row and ignoring null revenue; width is `request['window']` (2, 3, or 4).

Row-producing operations preserve row order and existing columns, adding derived fields. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

The interface assumes numeric units/prices/targets and ISO-like date strings. Duplicate lookup keys follow the dependency implementation's last-entry behavior.
