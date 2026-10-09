# Tabular service adapters

This package exposes six functions, each with signature `(rows, lookup, request)`;
all return new lists/dictionaries and preserve input objects. Implementation is
reused from the independently service-verified `published.a04_r01` package.

* `clean`: normalized (strip/lower) non-null regions and filled units.
* `revenue`: filled units and `revenue_cents` (null if units or price is null).
* `group`: normalized region/revenue aggregation, omitting null regions.
* `monthly`: month/region aggregation, omitting null grouping keys.
* `lookup`: appends `revenue_cents_per_target` from normalized region keys.
* `window`: appends trailing-row `roll_revenue_cents` mean.

Options: `request.fill` is `zero`, `mean`, or `median` (default `zero`; even
median averages central values; all-missing fills with zero). `request.agg` is
`sum`, `mean`, or `count` (default `sum`; count excludes null revenue; empty
sum/count are zero and empty mean is null). `request.window` is 2, 3, or 4.
Aggregate outputs are sorted by stringified keys. Unknown, null, or zero lookup
targets produce null. `lookup` is the lookup-table argument, distinct from the
function name. Invalid option values raise `ValueError`; rows are expected to
follow the service schema.

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
