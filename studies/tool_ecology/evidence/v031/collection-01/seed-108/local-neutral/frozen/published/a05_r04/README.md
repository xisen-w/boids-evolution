# Reusable table service aliases

This package exposes dependency-backed adapters for all six table service families, delegating to verified `published.a05_r03`. Public APIs all have signature `(rows, lookup, request)` and return newly allocated lists without modifying inputs:

* `clean(rows, lookup, request)`: normalize regions and fill missing units.
* `revenue(...)`: fill units and append revenue cents.
* `group(...)`: aggregate revenue by normalized region.
* `monthly(...)`: aggregate by month and normalized region.
* `lookup_service(...)`: append revenue per exact region target (named distinctly to avoid colliding with the lookup argument).
* `window(...)`: append trailing-row revenue means.

Fill policies are zero/mean/median; aggregate policies sum/mean/count. The underlying implementation defines missing-value and sorting behavior, with ISO date month extraction. Example: `revenue([{'units': None, 'price_cents': 8}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 8, 'revenue_cents': 0}]`.
