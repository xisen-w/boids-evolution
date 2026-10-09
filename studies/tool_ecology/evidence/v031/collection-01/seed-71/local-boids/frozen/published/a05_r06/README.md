# Row table services

Import the six adapters from `candidate`: `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window`. Each accepts `(rows, lookup, request)` and
returns a fresh list without mutating inputs. `rows` is a list of dictionaries;
`lookup` is the region-target-manager table and `request` configures the service.

* `clean`: preserve row columns and order; lowercase/strip region and fill
  missing units (`fill`: `zero`, `mean`, or `median`; all missing -> 0).
* `revenue`: same unit filling, append `revenue_cents` (None when either
  units or price is missing).
* `group`: normalize and derive revenue, then group by nonmissing region.
  `agg` is `sum`, `mean`, or `count`; count counts nonmissing revenue. Output
  is sorted by stringified region. Empty sum/count are 0; empty mean is None.
* `monthly`: group nonmissing month (`date[:7]`) and region, sorted by both
  stringified keys, with the same aggregation rules.
* `lookup`: append `revenue_cents_per_target` from exact normalized region
  lookup. Unknown region, missing/zero target, or missing revenue gives None.
* `window`: append trailing `roll_revenue_cents`, the mean over nonmissing
  revenues among the trailing `request['window']` ROWS including current;
  absent values do not extend the row window.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' N ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'n', 'sum_revenue_cents': 100}]
```

The implementation follows the documented request modes; invalid mode values
raise `ValueError`. Existing source columns and their insertion order are kept
before added derived columns on row-wise services. Dates are expected as ISO
`YYYY-MM-DD` strings.
