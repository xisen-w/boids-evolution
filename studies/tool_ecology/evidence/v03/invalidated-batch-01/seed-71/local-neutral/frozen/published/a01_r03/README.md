# Table services

Pure-Python services for row dictionaries. Each public adapter accepts `(rows, lookup, request)` and returns fresh dictionaries/lists without mutating inputs. Original columns and order are retained for row-shaped outputs; derived columns are appended.

- `clean`: strip/lower region and fill missing units using `request.fill` (`zero`, `mean`, `median`; defaults to `zero`; all missing becomes zero).
- `revenue`: fill units and derive `revenue_cents`, null if either operand is null.
- `group`: normalize region, derive revenue, aggregate by non-null region, sorted by string key. `request.agg` is `sum`, `mean`, or `count` (default `sum`); count ignores null revenue.
- `monthly`: same derivation, grouped on non-null month and region, month is first seven date characters.
- `lookup`: revenue output with `revenue_cents_per_target`, exact normalized region lookup; null for unknown/missing/zero target or null revenue.
- `window`: revenue output with mean of non-null revenue in trailing physical rows including current; width is `request.window` (default 2).

Empty sum/count groups yield zero, empty means null. Lookup duplicate normalized regions use the last entry. Numeric inputs are expected for arithmetic, dates should be ISO-like strings. Invalid fill/aggregation names raise ValueError.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'agg':'sum'}) == [{'region':'north','sum_revenue_cents':100}]
```
