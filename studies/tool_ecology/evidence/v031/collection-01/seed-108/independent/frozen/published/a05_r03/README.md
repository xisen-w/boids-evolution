# a05_r03 — native row-table services

The package exposes six adapters, each with signature `(rows, lookup, request)` and returns fresh row dictionaries/lists without mutating inputs. Rows are list-of-dict tables; optional units, prices, regions and dates may be `None` as described by the service contract.

* `clean(rows, lookup, request)`: strips/lowercases region and fills missing units (`fill`: `zero`, `mean`, or `median`; all-missing becomes zero), preserving columns and order.
* `revenue(...)`: fills units and adds `revenue_cents`; preserves region spelling and existing columns/order.
* `group(...)`: normalized regions, derived revenue, groups nonmissing region keys and aggregates nonmissing revenue (`agg`: `sum`, `mean`, `count`).
* `monthly(...)`: groups normalized region and `date[:7]`, omitting missing keys.
* `lookup(...)`: normalized region and derived revenue plus `revenue_cents_per_target`; exact normalized region lookup, None for absent/zero targets or missing revenue.
* `window(...)`: adds trailing row-window mean `roll_revenue_cents` (`window`: 2, 3, or 4); region is unchanged.

Group outputs are sorted by stringified keys. Empty aggregate sum/count is zero and empty mean is None. Example:

```python
from candidate import clean, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 4}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 4}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

Limitations: expects the specified row schema and valid service parameter values; does not coerce numeric fields.
