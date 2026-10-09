# Row service dispatcher

This package re-exports the six pure service adapters from the declared dependency `published.a00_r01`; each accepts `(rows, lookup, request)` and returns a new result without mutating its inputs. Import direct functions (`clean`, `revenue`, `group`, `monthly`, `lookup`, `window`) or use `apply(family, rows, lookup_rows, request)` to select one by its exact string name. Unknown names raise `ValueError`.

Example:
```python
from candidate import apply
result = apply('revenue', [{'units': 2, 'price_cents': 30}], [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 60
```

Fill modes are zero/mean/median; aggregation modes sum/mean/count; window widths are 2/3/4. Regions are normalized where specified; lookup keys are exact. Inputs use lists of dictionaries and monthly dates are ISO strings. Service-specific output shape, null, sorting and aggregation behavior follows the six recurring service definitions. Unsupported request modes raise `ValueError`.
