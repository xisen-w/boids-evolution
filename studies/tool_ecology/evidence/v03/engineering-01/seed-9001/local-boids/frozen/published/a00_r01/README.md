# Table services

Import the family adapters from `candidate`; each has the API `(rows, lookup, request)` and returns new dictionaries without mutating its inputs. Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Adapters: `clean` normalizes region and fills units; `revenue` additionally derives `revenue_cents`; `group` returns region plus the requested aggregate revenue column; `monthly` returns month/region aggregates; `lookup` adds `revenue_cents_per_target` from exact normalized region keys; `window` adds the trailing-row mean `roll_revenue_cents`. Request options are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (positive integer). All-missing units fill to zero. Missing revenue operands yield `None`; groups omit missing keys and aggregation ignores missing revenues. Lookup assumes lookup region keys are already normalized. Invalid option values raise `ValueError`.
