# Tabular services

Dependency-free native Python implementations. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list of dictionaries and does not mutate its inputs. Unused lookup arguments are accepted for a consistent adapter signature.

`request.fill` is `zero`, `mean`, or `median` (default `zero`); missing units are imputed from all available row units, with all-missing becoming zero. `request.agg` is `sum`, `mean`, or `count` (default `sum`). `request.window` must be 2, 3, or 4. Revenue is units multiplied by `price_cents`, or `None` if either operand is missing.

`clean` normalizes non-null region strings using strip/lower and imputes units. `revenue` imputes units and adds `revenue_cents`. `group` and `monthly` return aggregate records, dropping null grouping keys; monthly truncates date to its first seven characters. `lookup` adds `revenue_cents_per_target`, matching normalized region keys against normalized lookup region keys; missing/zero targets and missing revenue produce `None`. `window` adds the trailing-row mean of nonmissing revenue, including the current row.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
Limitations: inputs are expected to follow the described mapping/list schema; date values are sliced as strings rather than calendar-validated. Invalid fill/agg/window options raise `ValueError`.
