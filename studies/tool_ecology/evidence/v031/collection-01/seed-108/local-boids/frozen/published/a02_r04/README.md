# Candidate row-table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from
`candidate`. Each has signature `service(rows, lookup, request)` and returns
new dictionaries without mutating inputs. These functions delegate to the
native implementation in `published.a00_r01` (declared dependency `a00_r01`).

- `clean`: normalize region with strip/lower and fill missing units.
- `revenue`: fill units and append/derive `revenue_cents`.
- `group`: aggregate nonmissing revenue by normalized region, excluding null regions.
- `monthly`: aggregate by month and normalized region, excluding null keys.
- `lookup`: append `revenue_cents_per_target` using exact normalized region lookup;
  does not add target or manager columns.
- `window`: append mean revenue in trailing ROWS including current.

Requests support fill `zero`, `mean`, or `median` (all-missing fills with zero),
aggregation `sum`, `mean`, or `count`, and window widths 2, 3, or 4. Example:

```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 30}], [], {'fill': 'zero'}) == [
    {'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
```

Rows and lookup data are expected to be lists of dictionaries; monthly dates are
ISO strings. Unsupported request values raise `ValueError`.
