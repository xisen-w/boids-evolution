# Row service facade

Import any service with `from candidate import clean, revenue, group, monthly, lookup, window`. Each public function has signature `(rows, lookup, request)` and returns a new list of dictionaries. The facade delegates to verified `published.a00_r05` (and its declared dependency); it adds no independent behavior.

- `clean`: normalize region with strip/lower; fill missing units using request `fill` (`zero`, `mean`, `median`; all missing becomes zero).
- `revenue`: applies fill and adds `revenue_cents`.
- `group`: normalize and derive revenue, then aggregate by region using request `agg` (`sum`, `mean`, `count`), excluding missing keys/revenue.
- `monthly`: same revenue semantics, grouped by month and region.
- `lookup`: adds `revenue_cents_per_target` from exact normalized region lookup.
- `window`: adds trailing-ROWS mean `roll_revenue_cents`, using request `window`.

Example:
```python
from candidate import revenue
rows = [{"region": " West ", "units": None, "price_cents": 12}]
out = revenue(rows, [], {"fill": "zero"})
assert out[0]["region"] == "west" and out[0]["revenue_cents"] == 0
```
Inputs are not intentionally mutated. Detailed edge semantics and limitations follow the dependency's API; this wrapper does not independently validate arguments.
