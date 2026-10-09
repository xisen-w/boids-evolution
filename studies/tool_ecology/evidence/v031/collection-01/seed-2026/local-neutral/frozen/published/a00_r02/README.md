# Sales table service adapters

Native Python package exposing six functions, each with signature
`function(rows, lookup, request)`. Functions return new row dictionaries (or
aggregated rows) without mutating inputs. The implementation is reused from
`published.a05_r01`.

* `clean`: normalize non-null region strings using strip/lower and fill missing units.
* `revenue`: fill units and derive `revenue_cents` (`None` if units or price is missing).
* `group`: aggregate nonmissing revenue by normalized region, dropping missing keys.
* `monthly`: aggregate by month (`date[:7]`) and normalized region, dropping missing keys.
* `lookup`: add `revenue_cents_per_target` using normalized exact region matches; does not add target/manager.
* `window`: add mean revenue over trailing `request.window` rows including current.

Example:
```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

`request.fill` accepts `zero`, `mean`, or `median`; even medians average the
central values and all-missing fills resolve to zero. `request.agg` accepts
`sum`, `mean`, or `count` (count excludes missing revenue). Empty group sums and
counts are zero; empty means are `None`. `request.window` accepts 2, 3, or 4.
Unknown lookup regions, zero or missing targets, and missing revenue produce
`None` per target. Rows are expected to be dictionaries with service fields;
missing numeric values should be represented by `None`.
