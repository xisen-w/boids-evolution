# Sales transformations: stable service facade

Native Python facade reusing the verified implementation in `a05_r01`; it adds no third-party dependencies and does not mutate input rows, lookup entries, or request. All public adapters take `(rows, lookup, request)` and return fresh output rows/lists.

```python
from candidate import clean, revenue, group, monthly, lookup_service, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None,
         'price_cents': 20}]
cleaned = clean(rows, [], {'fill': 'zero'})
assert cleaned[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

`clean` strips/lowercases nonmissing regions and fills missing units. `revenue` also adds `revenue_cents`; a missing operand makes revenue `None`. `group` aggregates by normalized region and `monthly` by month and normalized region, omitting missing group keys. Both return only grouping columns and `<agg>_revenue_cents`. `lookup_service` adds per-target revenue using normalized exact region matches; missing/zero targets and missing revenue produce `None`. `window` adds mean revenue over the trailing `request.window` rows, including the current row.

`request.fill` is `zero`, `mean`, or `median` (even medians average the central values; all missing fills as zero). `request.agg` is `sum`, `mean`, or `count` (count excludes missing revenue). `request.window` is 2, 3, or 4. Defaults are zero, sum, and 2. Empty sum/count groups yield zero and empty means `None`. Missing numeric values are `None`. Inputs are lists of dictionaries with the service fields; malformed field types are outside the API contract. `lookup_service` is named distinctly to avoid shadowing the lookup data argument, and is the lookup adapter registered in `publish.json`.
