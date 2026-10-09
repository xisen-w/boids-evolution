# Tabular service adapters

The package exports six functions, each with signature `function(rows, lookup, request)`. Inputs are lists of dictionaries; returned data are newly allocated and inputs are not mutated. All normalize string regions with `strip().lower()`.

* `clean(rows, lookup, request)`: returns all input columns with units filled per `request['fill']` (`zero`, `mean`, or `median`); all-missing units become zero.
* `revenue(...)`: same unit fill, plus `revenue_cents` (null if units or price is null).
* `group(...)`: groups by normalized, non-null region; returns sorted region and `<agg>_revenue_cents` records.
* `monthly(...)`: groups by month (`date[:7]`) and non-null normalized region; sorted by month, then region.
* `lookup(...)`: adds `revenue_cents_per_target`, using normalized exact region keys from lookup records. Missing region matches, target, zero target, or revenue yield null. Does not add target/manager.
* `window(...)`: adds rolling mean `roll_revenue_cents` over trailing `request['window']` rows including current, ignoring null revenue values.

Group and monthly take `request['agg']` as `sum`, `mean`, or `count`; count counts non-null revenue. Empty mean is null; empty sum/count is zero (empty groups are not emitted). Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
request = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], request)[0]['revenue_cents'] == 0
assert group(rows, [], request) == [{'region': 'west', 'sum_revenue_cents': 0}]
```

Required fields are expected as described by the service contract; `request` must include fill and, for aggregations/window, agg/window respectively. Dates are expected as ISO strings.
