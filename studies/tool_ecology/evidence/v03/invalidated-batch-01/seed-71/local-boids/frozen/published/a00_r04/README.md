# Row service facade

Public functions all have signature `(rows, lookup, request)` and return fresh
lists of dictionaries without modifying inputs:

* `clean`: normalized region and filled units; preserves row columns/order.
* `revenue`: clean plus `revenue_cents` (null if units or price is null).
* `group`: aggregate revenue by normalized region, omit missing keys.
* `monthly`: aggregate by `month` (`date[:7]`) and region.
* `lookup`: add per-target revenue using exact normalized region matching.
* `window`: add trailing row-window mean of available revenue.

`request.fill` is `zero`, `mean`, or `median` (all-missing becomes zero);
`request.agg` is `sum`, `mean`, or `count`; `request.window` is 2, 3, or 4.
Group outputs use `<agg>_revenue_cents`; sum/count empty aggregates are zero,
mean with no values is null. Lookup adds no lookup-table fields; unknown regions,
null/zero targets, and null revenue yield null. Region strings are stripped and
lowercased. The API expects the specified row and lookup schemas and valid
parameter values; it does not validate malformed inputs.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```
