# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each accepts row dictionaries, a lookup-row list, and a request dictionary,
returns a new list of dictionaries, and leaves inputs unchanged.

- `clean`: lowercases and strips non-null region strings; fills missing units.
- `revenue`: fills units and appends `revenue_cents` (None if units or price is missing).
- `group`: groups normalized non-null regions; aggregates nonmissing revenue.
- `monthly`: groups by month (`date[:7]`) and normalized region; missing keys dropped.
- `lookup`: appends `revenue_cents_per_target` using exact normalized region lookup;
  absent/zero targets or missing revenue yield None.
- `window`: appends `roll_revenue_cents`, trailing ROWS mean including current.

`request.fill` supports `zero`, `mean`, or `median` (default `zero`; all-missing -> 0).
`request.agg` supports `sum`, `mean`, or `count` (default `sum`).
`request.window` supports 2, 3, or 4. Revenue is units times price_cents.
Example:
```python
from candidate import revenue
revenue([{"units": None, "price_cents": 5}], [], {"fill": "zero"})
# [{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
Rows are expected to be dictionaries and dates ISO-like strings. Invalid fill,
aggregate, or window values raise ValueError. This package delegates to the
verified `a02_r03` implementation and its declared dependency.
