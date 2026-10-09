# rowservices

Pure-Python, non-mutating adapters for the recurring row-table services. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are lists of dictionaries and request/lookup are ordinary dictionaries/lists. Unused arguments are retained for a uniform adapter signature.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`fill` must be `zero`, `mean`, or `median`; mean/median use observed units and all-missing units fill with zero. `agg` must be `sum`, `mean`, or `count`. Window sizes are 2, 3, or 4 trailing rows including current. Regions are stripped and lowercased (non-string missing values remain unchanged). Lookup keys are normalized the same way as row regions. The implementations assume numeric units/prices/targets and ISO date strings when present. They do not add lookup target or manager fields. Group outputs omit missing keys; revenue/count empty aggregates are zero and mean is None.
