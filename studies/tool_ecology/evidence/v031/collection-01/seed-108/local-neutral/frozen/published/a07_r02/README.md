# Native table transformations

Import adapters from `candidate` (or this package's publication name). Each public function accepts `(rows, lookup, request)` and returns a new list of row dictionaries without modifying inputs. Functions are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

`clean` normalizes regions and fills missing units. `revenue` fills units and appends `revenue_cents` without normalizing regions. `group` and `monthly` normalize regions, derive revenue, and return aggregates; group rows have `region` and `<agg>_revenue_cents`, monthly rows additionally have `month`. `lookup` normalizes regions and appends `revenue_cents_per_target`, using exact normalized region matches; it does not append target or manager. `window` derives revenue without region normalization and appends `roll_revenue_cents`, the mean of nonmissing revenues in the trailing request.window rows including current.

Example:
```python
from candidate import revenue
revenue([{'region': ' NORTH ', 'units': 2, 'price_cents': 30}], [], {'fill': 'zero'})
# [{'region': ' NORTH ', 'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
```

`fill` supports `zero`, `mean`, and `median` (even medians average the central pair; all missing fills with zero). Aggregation supports `sum`, `mean`, `count`; count excludes missing revenue, empty sum/count are zero, empty mean is None. Window widths supported are 2, 3, and 4. Dates are expected as ISO strings; missing dates/regions are excluded from monthly groups. Unsupported options raise `ValueError`.
