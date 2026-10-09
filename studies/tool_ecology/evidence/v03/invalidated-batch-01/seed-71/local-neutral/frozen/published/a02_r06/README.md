# Row services

Native Python adapters for six tabular service families. Every public function accepts
`(rows, lookup, request)` and returns a newly constructed result without modifying
any input. Input records are dictionaries following the service schema; lookup targets
are matched by exact normalized region. Region normalization is strip/lower.

* `clean(rows, lookup, request)`: preserve row/column order, normalize region and fill
  missing units (`request['fill']`: `zero`, `mean`, or `median`; all missing becomes 0).
* `revenue(...)`: clean plus `revenue_cents`, null if units or price is missing.
* `group(...)`: group non-null normalized regions; `request['agg']` is `sum`, `mean`,
  or `count`; output sorted by stringified region.
* `monthly(...)`: group by `date[:7]` and normalized region, dropping missing keys;
  sorted by stringified keys.
* `lookup_service(...)`: adds revenue per exact region target; missing/zero target or
  revenue gives null. Does not expose target or manager columns.
* `window(...)`: adds trailing ROWS mean of available revenues; requires
  `request['window']` (2, 3, or 4).

Aggregations count nonmissing revenue; empty aggregate behavior follows the service
contract (sum/count zero, mean null). Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
```

This package delegates to `published.a02_r05`, a verified implementation. Inputs are
expected to conform to the documented schema; no general-purpose schema validation is
provided.
