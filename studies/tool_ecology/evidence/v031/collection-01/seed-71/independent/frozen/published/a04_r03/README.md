# Tabular row services

Native Python, no third-party dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`. Matching `serve_clean`, `serve_revenue`, `serve_group`, `serve_monthly`, `serve_lookup`, and `serve_window` are thin service adapters with the same arguments.

All functions return new dicts/lists and leave arguments unmodified. `request.fill` is `zero`, `mean`, or `median` (default zero); all-missing units fill with zero. `request.agg` is `sum`, `mean`, or `count` (default sum); count ignores missing revenues. `request.window` is 2, 3, or 4 positional rows. Clean normalizes string regions by strip/lower and fills units. Revenue fills units and appends revenue without normalizing region. Group, monthly, and lookup normalize region. Group/monthly drop missing grouping keys and return only grouping and aggregate columns. Lookup appends the per-target ratio, without lookup metadata. Window appends positional trailing revenue mean. Aggregate output sorts by stringified keys. Sum/count empty groups are zero and mean is None.

Example:
```python
from candidate import revenue, group
rows = [{'region': 'North', 'units': None, 'price_cents': 5}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 0}]
```
Inputs are expected to be schema-conforming mappings and valid request parameters; malformed schemas are not coerced.
