# a06_r01

Native Python, dependency-free table transforms. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`; all are exported from the package root. Each returns new dictionaries and does not mutate its inputs. `lookup` is the table lookup argument name as well as the lookup-family function name.

`clean` normalizes non-null regions with strip/lower and fills null units using `request['fill']` (`zero`, `mean`, or `median`; empty inputs fill with zero). `revenue` does the same and appends `revenue_cents`, null when price or units is null. `group` groups non-null normalized regions; `monthly` groups by non-null YYYY-MM month and region. Both use `request['agg']` (`sum`, `mean`, `count`) and sort keys. `lookup` appends `revenue_cents_per_target`, using normalized region keys in the supplied lookup records. `window` appends the trailing-row mean in `roll_revenue_cents`, with width 2, 3, or 4 from `request['window']`.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Aggregates ignore null revenue; empty sum/count are zero and empty mean is null. Inputs are expected to be lists of mappings with the documented service fields and valid request modes. No external dependencies.
