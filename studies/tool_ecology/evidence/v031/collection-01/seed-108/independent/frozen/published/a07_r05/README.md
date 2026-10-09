# Tabular service adapters

This package exposes six pure-Python functions, each with the exact signature
`function(rows, lookup, request)`. They return new lists/dictionaries and do not
mutate the supplied rows, lookup, or request. The implementations are reused
from `published.a07_r04` (declared package dependency).

* `clean(rows, lookup, request)`: strip/lower non-null regions and fill missing
  units; all input columns and row order are retained.
* `revenue(...)`: fill missing units and append `revenue_cents`; region is not
  normalized. Missing units are filled before calculating revenue.
* `group(...)`: normalize region, calculate revenue, drop null region groups,
  and return region plus `<agg>_revenue_cents`, sorted by stringified region.
* `monthly(...)`: likewise, grouping by `date[:7]` and region and dropping rows
  with either key null; sorted by stringified keys.
* `lookup(...)`: normalize region, calculate revenue, append
  `revenue_cents_per_target`; exact region match only, null for absent/null/zero
  target or missing revenue. It does not add target or manager columns.
* `window(...)`: calculate revenue without region normalization and append
  `roll_revenue_cents`, a mean over nonmissing revenues in the trailing ROWS
  window including current row (null if that window has no values).

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`); an
all-missing units column fills with zero. Even-sized medians average the two
central values. `request.agg` accepts `sum`, `mean`, or `count` (default `sum`);
count counts nonmissing revenue, and empty sum/count groups are zero while an
empty mean is null. `request.window` accepts 2, 3, or 4. Invalid options raise
`ValueError`. Input rows are expected to be mappings with the service schema;
monthly dates are ISO date strings. No external dependencies are required
beyond the declared published package.

Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
