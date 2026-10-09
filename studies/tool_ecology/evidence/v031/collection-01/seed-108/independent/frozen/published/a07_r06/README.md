# Tabular service adapters

Public API: six functions with signature `name(rows, lookup, request)`, imported
from `candidate` (or this package's published name). All return fresh row
mappings and do not mutate inputs. Implementations are reused from
`published.a07_r04`; this package intentionally adds no alternate logic.

* `clean`: strip/lower non-null region and fill missing `units`; preserve all
  columns and order.
* `revenue`: fill missing units and append `revenue_cents` (units times
  `price_cents`, or null if either operand is null); region is unchanged.
* `group`: normalize region, derive revenue, drop missing region keys, aggregate
  nonmissing revenue; output `region` and `<agg>_revenue_cents`, sorted by
  stringified region.
* `monthly`: as group, grouping by `date[:7]` and region; drop missing keys and
  sort by stringified month/region.
* `lookup`: normalize region, derive revenue, append
  `revenue_cents_per_target` using exact region matches. Unknown/null/zero
  target or null revenue gives null; target and manager aren't added.
* `window`: derive revenue, append `roll_revenue_cents`, the mean of non-null
  revenue in the trailing `request.window` rows including current (null for an
  empty window).

`request.fill` supports `zero`, `mean`, `median` (all missing becomes zero;
median of an even count averages its central pair). `request.agg` supports
`sum`, `mean`, `count`; count counts non-null revenue, and empty groups return
zero for sum/count and null for mean. `request.window` supports 2, 3, or 4.
Invalid options raise `ValueError`. Rows use the described service schema and
monthly dates should be ISO strings. No additional external dependencies.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
