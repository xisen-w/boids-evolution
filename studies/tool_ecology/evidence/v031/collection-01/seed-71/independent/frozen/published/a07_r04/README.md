# Row-oriented table services

This package provides six dependency-backed public functions:
`clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`,
`group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`.
The `lookup_rows` argument is ignored except by the `lookup` service. Functions
return new dictionaries and do not mutate their inputs. Implementations are
re-exported from the declared dependency `published.a07_r03`.

`clean` normalizes region using strip/lower and fills null units. `revenue`
appends revenue_cents. `group` and `monthly` aggregate nonmissing revenue by
region and month/region respectively, excluding missing keys. `lookup`
normalizes region and appends revenue_cents_per_target (without adding target
or manager). `window` appends the mean of nonmissing revenue in the trailing
`request.window` rows, including the current row.

Request options: `fill` is `zero`, `mean`, or `median` (default `zero`; all
missing fills with zero); `agg` is `sum`, `mean`, or `count` (default `sum`,
count excludes missing revenue); and `window` is a positive integer row count
(default 2). Empty aggregation results are 0 for sum/count and None for mean.
Lookup returns None for unknown region, missing/zero target, or missing revenue.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'count'}) == [
    {'region': 'west', 'count_revenue_cents': 1}
]
```
Limitations: input rows are expected to contain the service schema fields;
monthly expects ISO-like date strings (month is the first seven characters).
