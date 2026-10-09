# Tabular row services

The package root exports six pure adapters. Every function takes
`(rows, lookup, request)` and returns a new list of dictionaries without
mutating its inputs:

* `clean(rows, lookup, request)`: strip/lower string regions and fill missing
  units.
* `revenue(...)`: fill units and add `revenue_cents` (None if units or price
  is None).
* `group(...)`: normalize regions, derive revenue, and aggregate by region.
* `monthly(...)`: same derivation, grouped by `date[:7]` and region.
* `lookup(...)`: add `revenue_cents_per_target` from exact normalized-row-region
  lookup keys; lookup keys themselves are not normalized.
* `window(...)`: add trailing-row mean `roll_revenue_cents`.

Example:

```python
import candidate
candidate.revenue(
    [{'units': None, 'price_cents': 25}], [], {'fill': 'zero'}
)
# [{'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
```

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`); all
missing units become zero. `request.agg` accepts `sum`, `mean`, or `count`
(default `sum`); count excludes missing revenues. Empty means are `None`.
`request.window` must be 2, 3, or 4. Window width counts rows, including rows
whose revenue is missing. Missing grouping keys are dropped. Inputs are lists
of dictionaries with the service fields; dates are expected as ISO strings.
