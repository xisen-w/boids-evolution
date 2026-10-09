# Native row-table transforms

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from
`candidate`. Each public function has the same exact signature
`function(rows, lookup, request)`, where rows/lookup are lists of dictionaries
and request is a dictionary. The returned data is newly allocated; input
records and arguments are not mutated. Original row key order is retained, and
new derived fields are appended. Aggregated results contain only their documented
keys.

* `clean(rows, lookup, request)`: strip and lowercase string regions, and fill
  null units according to `request['fill']` (`zero`, `mean`, or `median`; default
  `zero`). All-null units fill with zero.
* `revenue(...)`: same preparation, then append `revenue_cents` as units times
  price, or `None` when price/units is missing.
* `group(...)`: aggregate non-null revenue by non-null normalized region using
  `request['agg']` (`sum`, `mean`, `count`; default `sum`). Output is sorted by
  stringified region. Empty mean is `None`; sum/count are zero.
* `monthly(...)`: as group, partitioning on non-null `date[:7]` and region;
  output sorted by stringified month and region.
* `lookup(...)`: append `revenue_cents_per_target`, using an exact lookup-region
  key match. Missing/unknown/zero target or missing revenue gives `None`.
  Lookup manager and target columns are not added to output.
* `window(...)`: append trailing-row `roll_revenue_cents`, the mean of available
  revenues in the current row and up to `request['window']-1` preceding rows.
  Window defaults to 2 and must be 2, 3, or 4.

Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 150}]
print(group(rows, [], {'fill': 'zero', 'agg': 'sum'}))
# [{'region': 'west', 'sum_revenue_cents': 300}]
```

This package expects numeric units, prices, and targets when non-null, string
regions/dates as described by the service schema, and supported request values.
It raises `ValueError` for unsupported fill, aggregate, or window settings.
