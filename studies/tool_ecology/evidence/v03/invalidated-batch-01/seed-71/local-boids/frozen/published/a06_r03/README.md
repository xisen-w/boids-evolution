# Row service adapters

Six public adapters accept `(rows, lookup, request)` and return the full output for their respective clean, revenue, group, monthly, lookup, or window service. `transform(family, rows, lookup_rows, request)` dispatches by one of those exact family names and raises `KeyError` for unknown names. This native package reuses the verified `published.a06_r02` implementation, which in turn depends on `published.a00_r01`.

Example:
```python
from candidate import transform
out = transform("revenue", [{"region":" West ", "units":2, "price_cents":50}], [], {"fill":"zero"})
# [{'region': 'west', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
Missing-unit fills are zero/mean/median; aggregates are sum/mean/count; windows are trailing ROWS windows of the requested size. Group outputs omit missing keys and sort lexically. Lookup uses exact normalized region keys. Inputs are not mutated. Input schema/validation behavior and missing-value semantics are inherited from the dependency; this facade adds no independent validation.
