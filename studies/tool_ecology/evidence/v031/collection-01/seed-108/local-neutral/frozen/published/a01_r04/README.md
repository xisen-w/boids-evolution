# Row-table services

This package exposes six reusable pure row-table adapters. Each has the exact
signature `(rows, lookup, request)` and returns a new list without mutating its
inputs. `rows` is a list of dictionaries; `lookup` is a list of region/target/
manager dictionaries. Requests use `fill` (`zero`, `mean`, or `median`) for
missing units, `agg` (`sum`, `mean`, or `count`) for aggregate services, and
`window` (2, 3, or 4) for the window service.

* `clean_service`: normalize region with strip/lower and fill missing units.
* `revenue_service`: fill units and append `revenue_cents`.
* `group_service`: aggregate revenue by normalized region.
* `monthly_service`: aggregate revenue by month and normalized region.
* `lookup_service`: append revenue divided by the exact normalized-region target.
* `window_service`: append trailing-row mean revenue.

Example:

```python
from candidate import revenue_service
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
result = revenue_service(rows, [], {'fill': 'zero'})
# result[0]['region'] == 'west'; result[0]['revenue_cents'] == 0
```

Missing operands produce missing revenue; missing group keys are omitted.
Aggregates exclude missing revenue (empty sum/count are zero, empty mean is
None). Lookup uses exact normalized region keys; absent/zero targets yield
None. Window means use nonmissing revenues among the trailing rows, including
the current row; a window with no values yields None. All-missing unit fills
are zero and even-sized medians average the two central values. These APIs are
for the stated list-of-dicts schema and valid request modes, not arbitrary
DataFrame or streaming inputs.
