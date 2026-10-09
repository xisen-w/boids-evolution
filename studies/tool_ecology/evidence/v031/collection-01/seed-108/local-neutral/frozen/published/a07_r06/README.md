# Table services

Dependency-free native Python API. All six public functions accept `(rows, lookup, request)` and return newly allocated lists/dictionaries without mutating inputs. `lookup` means the auxiliary lookup table and is ignored except by `lookup`.

* `clean(rows, lookup, request)`: strip/lowercase string regions; fill missing units via `fill` (`zero`, `mean`, or `median`, default `zero`). Keeps columns and row order.
* `revenue(...)`: fill missing units and append `revenue_cents`; this service leaves region strings unchanged. Revenue is `None` if units or price is missing.
* `group(...)`: normalized region/revenue aggregate, omitting missing regions. `agg` is `sum`, `mean`, or `count` (default `sum`); missing revenue is excluded.
* `monthly(...)`: normalized region and revenue, then group by month (`date[:7]`) and region; missing keys are excluded. Result is sorted by stringified keys.
* `lookup(...)`: normalized region/revenue, then append `revenue_cents_per_target` using exact normalized region matching. Unknown/missing/zero targets and missing revenue produce `None`; lookup metadata is not appended.
* `window(...)`: revenue with unchanged region, then append trailing-ROWS mean `roll_revenue_cents`; `window` must be 2, 3, or 4.

All-missing units are filled with zero. Even medians average the two center values. Empty aggregate groups yield 0 for sum/count and `None` for mean. Example:

```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 4, 'region': ' X '}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'units': 0, 'price_cents': 4, 'region': ' X ', 'revenue_cents': 0}
]
```

Inputs are lists of mappings/dictionaries with numeric operands (or `None`); dates are ISO-like strings. Invalid fill/aggregate/window options raise `ValueError`.
