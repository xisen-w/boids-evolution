# Table service facade

Native Python facade for the six row-oriented service APIs. It delegates directly to the verified `published.a04_r02` package (declared dependency), so behavior and validation are defined by that implementation.

Each public function has the common signature `function(rows, lookup, request)` and returns a new list of dictionaries without mutating inputs:

* `clean`: normalized regions and imputed units.
* `revenue`: imputed units and derived `revenue_cents`.
* `group`: aggregate revenue by region.
* `monthly`: aggregate revenue by month and region.
* `lookup`: add revenue per normalized-region target.
* `window`: add trailing row-window mean revenue.

Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```

Requests use `fill` values `zero`, `mean`, or `median`; aggregations accept `sum`, `mean`, or `count`; window uses a positive integer width (service requests specify 2, 3, or 4). Null revenue is excluded from aggregates. Empty means and unavailable lookup/window results are `None`; sum/count empty aggregates are zero. The API expects list-of-dict inputs matching the service schema; it does not validate arbitrary schemas beyond the delegated implementation.
