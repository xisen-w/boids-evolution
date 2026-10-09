# Tabular service adapters

Import the package root (`import candidate`). Each public adapter accepts `(rows, lookup, request)` and returns new dictionaries without mutating inputs:

- `clean(rows, lookup, request)`: normalizes string regions with strip/lower and fills missing units.
- `revenue(...)`: fills units and adds `revenue_cents`.
- `group(...)`: groups normalized regions and aggregates revenue.
- `monthly(...)`: groups by month and normalized region.
- `lookup(...)`: adds `revenue_cents_per_target` using exact keys in the lookup table.
- `window(...)`: adds a trailing row-window revenue mean.

Example: `candidate.revenue([{'units': 2, 'price_cents': 30}], [], {'fill': 'zero'})` returns `[{'units': 2, 'price_cents': 30, 'revenue_cents': 60}]`.

Requests use `fill` = `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. Grouping requests use `agg` = `sum`, `mean`, or `count` (default `sum`). Window requests use width 2, 3, or 4. Group means with no nonmissing revenue are `None`; empty sum/count groups cannot arise because groups are formed from rows. Dates are expected as ISO strings. Lookup regions are matched exactly after row region normalization; lookup keys themselves are not normalized. Inputs are expected to be lists of dictionaries with the documented service fields.
