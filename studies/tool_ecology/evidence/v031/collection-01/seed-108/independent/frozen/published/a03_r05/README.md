# Row-table service adapters

The package root exports `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. Each has the signature `function(rows, lookup, request)` and returns a new list of row dictionaries without mutating its inputs. Implementations are re-exported from the received, service-verified `published.a03_r03` package.

- `clean`: strip/lower region and fill missing units; retains every column and row order.
- `revenue`: fill missing units, calculate `revenue_cents` (null when either operand is null); retains original columns/order.
- `group`: normalized region and revenue, aggregate non-null revenue by non-null region; returns region and `<agg>_revenue_cents`.
- `monthly`: additionally groups by `date[:7]`; excludes missing grouping keys and sorts output lexically by stringified keys.
- `lookup`: normalized region and revenue, adds `revenue_cents_per_target` from exact region-key lookup; does not append target or manager.
- `window`: adds `roll_revenue_cents`, the mean of non-null revenue in the trailing `request['window']` rows including current.

Use `request['fill']` = `zero`, `mean`, or `median` (all-missing fills with zero; even median averages its two central values). Grouping requires `request['agg']` = `sum`, `mean`, or `count`; count counts non-null revenues. Empty sums/counts are zero and empty means are null. Window sizes supported are 2, 3, and 4. Invalid options raise `ValueError`.

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
result = revenue(rows, [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 250
```

Inputs are expected to follow the service schema (numeric values and required keys where relevant); this package adds no validation beyond its underlying adapters.
