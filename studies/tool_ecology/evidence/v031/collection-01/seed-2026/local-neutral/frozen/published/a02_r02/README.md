# Candidate row services

Native Python adapters for the six specified table service families. Public API:
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each takes a list of row dictionaries, lookup entries (or `None`), and request
mapping, and returns new dictionaries without mutating inputs. `request.fill`
is `zero`, `mean`, or `median`; aggregation is `sum`, `mean`, or `count`; window
width is 2, 3, or 4. See the service specification for output columns and null
semantics.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Implementation is reused from `published.a04_r01`; this package adds no
independent semantics or input-schema validation beyond that implementation.
