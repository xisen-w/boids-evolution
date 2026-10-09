# Row service facade

A dependency-light native Python facade over `published.a00_r01`, whose six
service families have verified service feedback. Import `candidate`; every
adapter accepts `(rows, lookup, request)` and returns a new list of row dicts.

* `clean(rows, lookup, request)` normalizes string regions with strip/lower
  and fills missing units.
* `revenue(...)` fills units and appends/sets `revenue_cents`.
* `group(...)` groups normalized nonmissing regions and aggregates revenue.
* `monthly(...)` groups by month and normalized region.
* `lookup(...)` adds `revenue_cents_per_target` based on exact lookup keys.
* `window(...)` adds `roll_revenue_cents`, the mean of nonmissing revenues
  in trailing ROWS including the current row.

Example:

```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 30}], [], {'fill': 'zero'}) == [
    {'units': 2, 'price_cents': 30, 'revenue_cents': 60}
]
```

`fill` is `zero`, `mean`, or `median` (default `zero`; all missing fills as
zero). `agg` is `sum`, `mean`, or `count` (default `sum`). `window` is 2, 3,
or 4. The delegated implementation assumes ISO date strings and list-of-dict
inputs. Lookup table region keys are exact and are not normalized. Empty
mean aggregates yield `None`; inputs are not mutated.
