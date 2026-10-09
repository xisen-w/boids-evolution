# Table service adapters

Import with `from candidate import clean, revenue, group, monthly, lookup_service, window`.
Every function accepts `(rows, lookup, request)` and returns a new list of row dictionaries; inputs are not mutated. `lookup` is reserved as an argument name, so the lookup family is exposed as `lookup_service`.

- `clean`: normalize region strings by stripping and lowercasing; fill missing units.
- `revenue`: fill missing units and add `revenue_cents`.
- `group`: aggregate revenue by normalized region, dropping missing region keys.
- `monthly`: aggregate by `month` and normalized region, dropping missing keys.
- `lookup_service`: add `revenue_cents_per_target` from exact normalized region matches; does not add lookup metadata.
- `window`: add the trailing-row mean `roll_revenue_cents`.

The `request` dictionary uses `fill`=`zero`, `mean`, or `median` (default `zero`), `agg`=`sum`, `mean`, or `count` (default `sum`), and `window` (default 2). Missing-value, empty-group, and ordering behavior follows the service specification. Example:

```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 150}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 150, 'revenue_cents': 300}]
```

Rows and lookup entries are expected to follow the documented service schema. Malformed requests and malformed records are not validated. Implementations are delegated to `published.a00_r02`.
