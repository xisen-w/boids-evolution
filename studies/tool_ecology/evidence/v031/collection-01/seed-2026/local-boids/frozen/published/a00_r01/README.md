# tabular_services

Pure-Python adapters for six row-table service families. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Inputs are lists of dictionaries; outputs are new dictionaries/lists and inputs are not modified. Requests support `fill` (`zero`, `mean`, `median`) and for group/monthly `agg` (`sum`, `mean`, `count`); window uses `window` (2, 3, or 4).

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Region normalization applies to clean/group/monthly and the row region used by lookup. Lookup table keys are matched exactly against that normalized row region. Missing dates/regions are excluded from grouped outputs; aggregation excludes missing revenue. No schema validation is performed.
