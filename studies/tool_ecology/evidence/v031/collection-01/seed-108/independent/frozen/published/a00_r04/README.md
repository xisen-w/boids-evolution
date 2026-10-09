# Row transform facade

Native Python facade for the six row-oriented table services. It delegates to `published.a00_r02`, declared as a dependency, and adds no transformation semantics.

## Public API

`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts rows and lookup as lists of dictionaries and request as a dictionary, returning a fresh list of dictionaries. Inputs are not mutated. `lookup` is the name of the lookup-service callable as well as its second argument.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Fill modes are zero, mean, and median (including midpoint median; all-missing fills with zero). Group aggregation supports sum, mean, and count. Window widths supported are 2, 3, and 4. Region normalization and aggregation/window details follow the received implementation. This facade requires `published.a00_r02` to be available; it does not provide standalone behavior without that dependency.
