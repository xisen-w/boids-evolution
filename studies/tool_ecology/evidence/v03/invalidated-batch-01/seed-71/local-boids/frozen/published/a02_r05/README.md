# Row service facade

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Each public function has the API `function(rows, lookup, request)` and returns a new list of row dictionaries; inputs are not modified. This package delegates to the verified `published.a00_r04` adapters, included as the declared dependency.

The input contract is the service contract: rows are dictionaries; `request.fill` is `zero`, `mean`, or `median`; `request.agg` is `sum`, `mean`, or `count`; `request.window` is the trailing row count. Clean normalizes region and fills units. Revenue also derives `revenue_cents`. Group and monthly aggregate revenue; lookup adds the per-target revenue; window adds trailing mean revenue. Missing values, empty input and sorting/column-order semantics follow the service definitions.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
result = revenue(rows, [], {'fill': 'zero'})
# result[0]['region'] == ' west '; result[0]['revenue_cents'] == 250
```
