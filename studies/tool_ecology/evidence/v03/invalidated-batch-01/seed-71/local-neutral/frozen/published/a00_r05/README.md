# Tabular service adapters

Native Python package exposing `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. All return fresh lists of dictionaries and
are backed by the declared dependency `published.a00_r04` (which depends on
`a00_r03`). Inputs are expected to be lists of row dictionaries, lookup rows,
and a request dictionary; the contract's fill options are `zero`, `mean`,
`median`, aggregations `sum`, `mean`, `count`, and window sizes 2, 3, 4.

`clean` normalizes regions and fills missing units; `revenue` also derives
revenue cents; `group` and `monthly` aggregate by region and month/region;
`lookup` adds revenue per target; `window` adds trailing row-window mean.
Derived and output column behavior follows the service contract. The package
adds no third-party dependencies. Unsupported request values are outside the
specified contract.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50, 'region': ' West '}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
