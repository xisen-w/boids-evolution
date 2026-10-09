# Row table services

Native-Python public adapters accept `function(rows, lookup, request)` and return a new list of row dictionaries (or grouped dictionaries); inputs are not mutated. This package delegates to the verified `a03_r03` implementation, which is declared as a dependency.

Functions: `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service`. Short aliases without `_service` are equivalent. `lookup` may be an empty list except for lookup service. Request options are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4), as relevant.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
result = revenue(rows, [], {'fill': 'zero'})
assert result[0]['region'] == 'west'
assert result[0]['revenue_cents'] == 250
```

Cleaning normalizes regions and fills missing units. Revenue derives `revenue_cents`; grouped services drop missing keys and aggregate nonmissing revenues. Lookup adds the revenue/target ratio, and window adds a trailing row-window mean. These functions expect dictionary rows with the documented service fields and valid option values; they do not validate schemas beyond their implementation's ordinary Python behavior.
