# Row-table services

This package re-exports the verified native implementation in `published.a06_r04` and declares that package as its dependency. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a fresh result and does not mutate input rows, lookup, or request.

`clean` normalizes region using strip/lower and fills missing units (`fill`: zero/mean/median; all missing -> 0). `revenue` fills units and appends revenue_cents, null if either operand is missing. `group`/`monthly` aggregate nonmissing revenue (`agg`: sum/mean/count), dropping missing keys and sorting stringified keys; monthly uses date[:7]. `lookup` adds revenue_cents_per_target by exact normalized-row-region to lookup-key match; unknown, absent/zero target, or null revenue gives null. `window` adds the mean of nonmissing revenue in trailing `window` rows including current (2/3/4), null when no values. Row services preserve original fields and order; group outputs aggregate fields only.

Example:
```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Inputs should follow the documented schemas and modes; invalid modes may raise `ValueError`. Lookup keys are exact and are not normalized. This package adds no behavior beyond the declared dependency.
