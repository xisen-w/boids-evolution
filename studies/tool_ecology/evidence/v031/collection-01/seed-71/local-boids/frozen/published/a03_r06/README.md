# Row-table services

Six non-mutating adapters accept `(rows, lookup, request)` and return fresh lists
of dictionaries. Public callables: `clean`, `revenue`, `group`, `monthly`,
`lookup`, and `window`.

* `clean`: strip/lower region strings and fill missing units via request `fill`
  (`zero`, `mean`, or `median`; all-missing becomes zero). Retains columns/order.
* `revenue`: clean/fill units and append `revenue_cents`, null if either operand
  is null; retains column/order.
* `group`: normalize/fill/derive revenue, drop missing regions, aggregate valid
  revenue using request `agg` (`sum`, `mean`, `count`).
* `monthly`: additionally derive month from the first seven date characters and
  group by month and region, dropping null keys.
* `lookup`: append revenue divided by exact normalized-region target; unknown,
  null/zero target, or null revenue produces null. Does not append lookup fields.
* `window`: append mean revenue over trailing request `window` rows (2, 3, or 4),
  ignoring null revenues; an empty valid window produces null.

Aggregations sort by stringified keys; count counts non-null revenue. Inputs are
service-shaped mappings. Invalid parameter values raise `ValueError`.

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
