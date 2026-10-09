# Row services (compatibility facade)

This package provides six root-level callables with signature
`service(rows, lookup, request)`, returning fresh output structures without
mutating inputs. It delegates to the verified `published.a06_r02` implementation
rather than reimplementing the service semantics.

* `clean(rows, lookup, request)`: normalize string regions and fill missing units.
* `revenue(...)`: fill units and append `revenue_cents`.
* `group(...)`: normalized regional revenue aggregation.
* `monthly(...)`: normalized month-and-region revenue aggregation.
* `lookup(...)`: normalized-region revenue per target lookup.
* `window(...)`: trailing row-window revenue mean.

Fill modes are `zero`, `mean`, and `median`; aggregations are `sum`, `mean`,
and `count`; window sizes are 2, 3, or 4. Defaults and exact column/key
ordering follow the delegated implementation. Example:

```python
from candidate import revenue
result = revenue([{'units': 2, 'price_cents': 150}], [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 300
```

The facade accepts the published row/request schemas and adds no validation or
semantics beyond its dependency. Requires `published.a06_r02` on the import path.
