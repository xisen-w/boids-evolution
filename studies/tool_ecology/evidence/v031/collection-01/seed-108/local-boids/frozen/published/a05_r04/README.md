# Row-table service facade

Exports six callables, each with the exact signature `service(rows, lookup, request)`:
`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. The adapters delegate to `published.a00_r01`, a declared dependency; this package does not duplicate its implementation. Inputs are expected to be the row dictionaries, lookup dictionaries, and request fields described below. The dependency provides non-mutating services.

* `clean`: normalize region (strip/lower), fill missing units; retain all columns and row order.
* `revenue`: clean plus `revenue_cents` derived from units and price.
* `group`: aggregate nonmissing revenue by normalized region.
* `monthly`: aggregate by month and normalized region.
* `lookup`: append revenue per exact normalized-region target match.
* `window`: append trailing row-window mean revenue.

Request uses `fill`=`zero`/`mean`/`median`, `agg`=`sum`/`mean`/`count`, and `window`=2/3/4 for applicable services. Example:

```python
from candidate import clean, lookup
rows = [{'region': ' West ', 'units': None, 'price_cents': 100}]
cleaned = clean(rows, [], {'fill': 'zero'})
# cleaned[0]['region'] == 'west'; cleaned[0]['units'] == 0
```

Limitations: all input and edge-case semantics follow the declared `published.a00_r01` dependency; this facade adds no independent validation or alternate behavior. Requires that dependency to be installed on the package path.
