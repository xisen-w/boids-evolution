# Native row services

All APIs accept `(rows, lookup, request)`, where rows and lookup are lists of dictionaries and request is a dictionary. Inputs are not mutated; outputs are fresh dictionaries. Public functions: `clean`, `revenue`, `group`, `monthly`, `lookup` (lookup service), and `window`.

`clean` normalizes string regions with strip/lower and fills missing units. `revenue` fills missing units and appends `revenue_cents`, but does not normalize regions. Fill policy is `request['fill']` (`zero`, `mean`, `median`; default zero); all-missing means/medians fill with zero. Missing price makes revenue None. `group` and `monthly` normalize regions and aggregate revenue, dropping missing grouping keys; `request['agg']` is sum/mean/count (default sum), with count excluding missing revenue and empty means None. Monthly uses the first seven date characters. Results are sorted by string keys.

`lookup` normalizes row regions and adds `revenue_cents_per_target`, using exact keys from lookup rows; absent, null, or zero target and null revenue yield None. It never adds lookup metadata. `window` does not normalize regions and adds trailing ROWS mean including current; `request['window']` must be 2, 3, or 4. Existing columns and order are retained, with new columns appended. Aggregation outputs are newly constructed.

Example:
```python
from candidate import revenue, group
r = [{'region': ' X ', 'units': 2, 'price_cents': 30}]
assert revenue(r, [], {'fill':'zero'})[0]['revenue_cents'] == 60
assert group(r, [], {'fill':'zero','agg':'sum'}) == [{'region':'x','sum_revenue_cents':60}]
```
