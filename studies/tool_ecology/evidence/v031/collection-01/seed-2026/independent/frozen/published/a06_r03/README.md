# Row service adapters

The public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` implement
all six requested service contracts. They are re-exports of the received,
service-verified pure-Python implementation `published.a06_r02`; inputs are not
mutated. `lookup` is the service function name (its second argument is the lookup
rows).

`request['fill']` supports `zero`, `mean`, and `median` (default `zero`); an
all-missing units column fills with zero. Revenue is units times price, or None
when price is None. Grouping services accept `request['agg']` of `sum`, `mean`,
or `count` (default `sum`); count excludes missing revenue. Monthly groups by
month and normalized region. Lookup uses exact normalized-region matching and
returns None for unknown/None/zero targets or missing revenue. Window uses the
trailing `request['window']` rows including current (2, 3, or 4), averaging only
nonmissing revenues within those rows. Existing row columns/order are preserved
where specified; aggregate outputs are newly constructed and sorted.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' X ', 'units': 2, 'price_cents': 30}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 60
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'x', 'sum_revenue_cents': 60}]
```
