# Verified row-table services

This package re-exports six pure-Python service adapters from `published.a03_r02`,
which has verified service results for all six families. Public functions are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`.

Inputs are lists of row dictionaries and a request dictionary. `request.fill`
may be `zero`, `mean`, or `median`; grouped services use `request.agg` in
`sum`, `mean`, `count`; window uses `request.window` in 2, 3, 4. Outputs are
new row dictionaries; callers' inputs are not modified. Clean normalizes regions
and fills units; revenue derives cents; group/monthly aggregate; lookup adds
revenue per target; window adds trailing-row revenue mean.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
result = revenue(rows, [], {'fill': 'zero'})
# result[0]['revenue_cents'] == 250
```

Behavioral details and validation are inherited from the documented received
implementation. No additional dependencies beyond `published.a03_r02`.
