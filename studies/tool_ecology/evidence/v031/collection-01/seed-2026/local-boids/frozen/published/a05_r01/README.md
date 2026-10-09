# Table transformations

Native Python package with six service adapters. Every public adapter accepts `(rows, lookup, request)`; input mappings are not mutated. Rows are copied, retain their original key ordering/values (except normalized `region` and filled `units`), and derived keys are appended.

* `clean(rows, lookup, request)`: strip/lower string regions and fill null units using `request['fill']` (`zero`, `mean`, or `median`; all-null becomes zero). Preserves row order and fields.
* `revenue(...)`: same normalization/fill, appends `revenue_cents`; it is null if units or price is null.
* `group(...)`: returns rows `{region, '<agg>_revenue_cents'}`, grouped on non-null normalized region; aggregation is `request['agg']` (`sum`, `mean`, `count`). Count excludes null revenues; empty sum/count are zero and empty mean is null.
* `monthly(...)`: same aggregation grouped on non-null `(date[:7], region)`; output keys are month, region, aggregate, sorted lexically.
* `lookup(...)`: appends `revenue_cents_per_target` using exact normalized region matches. Missing/zero targets and missing revenue produce null. Lookup manager/target fields are not added.
* `window(...)`: appends `roll_revenue_cents`, the mean of non-null revenues in trailing `request['window']` rows (2, 3, or 4), including current row.

Example:
```python
from candidate import revenue
rows = [{'region': ' WEST ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
Inputs are expected to be lists of dictionaries and the documented request keys. Date month extraction uses the first seven characters; input dates are expected in ISO format.
