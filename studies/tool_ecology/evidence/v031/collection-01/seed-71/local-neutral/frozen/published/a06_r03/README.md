# Table service facade

This package re-exports tested native table transformations from `published.a06_r02`;
its declared dependency is bundled with it. Public call signatures (all return fresh
lists and do not mutate arguments):

* `clean(rows, lookup, request)`: normalize region (strip/lower), fill missing units.
* `revenue(rows, lookup, request)`: fill units and append `revenue_cents`.
* `group(rows, lookup, request)`: aggregate revenue by nonmissing normalized region.
* `monthly(rows, lookup, request)`: aggregate by nonmissing month and normalized region.
* `lookup_revenue(rows, lookup, request)`: append revenue and per-target revenue.
* `window(rows, lookup, request)`: append trailing-row rolling revenue mean.

The `*_service` names are equivalent three-argument adapters; `lookup_service` is
also the lookup adapter. Requests support `fill` = `zero`, `mean`, or `median`
(default `zero`); `agg` = `sum`, `mean`, or `count` (default `sum`); and `window`
= 2, 3, or 4 (default 2). Unknown options raise `ValueError`. Missing values are
`None`; all-missing units fill with zero. Lookup matches normalized exact region keys.
Dates are expected to support `[:7]` for month extraction.

Example:
```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
