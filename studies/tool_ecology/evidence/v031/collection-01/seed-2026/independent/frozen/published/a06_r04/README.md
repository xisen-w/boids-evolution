# Row service adapters

This package provides six pure-Python functions, each with signature
`function(rows, lookup, request)`. They do not mutate their arguments. Functions
return fresh row dictionaries (or fresh aggregate rows), retaining input row
order wherever output is row-oriented.

* `clean`: lowercase/strip string regions and fill missing units; preserves all
  other fields. `request['fill']` is `zero`, `mean`, or `median` (default `zero`);
  all-missing units fill with zero.
* `revenue`: fills missing units and adds `revenue_cents=units*price_cents`,
  or `None` when either operand is missing. Original region is unchanged.
* `group`: normalized region, derived revenue and grouped nonmissing revenue;
  missing regions are dropped. Returns region and `<agg>_revenue_cents`.
* `monthly`: same, grouping by `date[:7]` and normalized region; missing group
  keys are dropped. Returns month, region, and aggregate field.
* `lookup`: normalized region and revenue plus
  `revenue_cents_per_target`; exact normalized region match is used. Missing
  revenue, unknown region, and absent/zero target produce `None`. Lookup
  metadata is not added to rows.
* `window`: adds `roll_revenue_cents`, the mean of nonmissing revenue in the
  trailing `request['window']` rows including the current row (2, 3, or 4).
  Missing revenues do not extend the window.

Aggregations accept `request['agg']` = `sum`, `mean`, or `count` (default
`sum`). Count excludes missing revenue; empty sum/count are zero and empty mean
is `None`. Aggregate results sort by stringified keys. Inputs are expected to
be lists of dictionaries and request/lookup mappings as described by the
service contract. The implementation is reused from the received, verified
`published.a06_r02` package.

```python
from candidate import revenue, group
rows = [{'region': ' X ', 'units': 2, 'price_cents': 30}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 60
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'x', 'sum_revenue_cents': 60}]
```
