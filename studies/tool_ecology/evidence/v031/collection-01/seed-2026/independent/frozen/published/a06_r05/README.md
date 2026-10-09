# Row service adapters

This package exposes six functions with the exact signature `f(rows, lookup, request)`. Each returns fresh dictionaries and does not mutate the supplied rows, lookup, or request. Row-oriented services preserve row order and input columns; aggregate services return fresh aggregate rows.

- `clean`: normalize string `region` using strip/lower and fill missing `units`; preserves all columns.
- `revenue`: fill missing units and add `revenue_cents`, null if units or price is null; region is not normalized.
- `group`: normalized region and derived revenue, grouped by non-null region.
- `monthly`: same, grouped by non-null month (`date[:7]`) and region.
- `lookup`: normalized region and revenue plus `revenue_cents_per_target`; exact normalized region matching, null for unknown/zero/null target or null revenue; no lookup metadata is added.
- `window`: derived revenue plus `roll_revenue_cents`, the mean over non-null revenues among trailing rows including current.

`request['fill']` supports `zero`, `mean`, and `median` (default `zero`); all-missing units fill as zero and even medians average the two middle values. Aggregations use `request['agg']` (`sum`, `mean`, or `count`, default `sum`); count excludes missing revenue, empty sum/count are zero, and empty mean is null. Aggregate keys sort by their string representation. Window width is `request['window']` and must be 2, 3, or 4. Inputs are lists of dictionaries and mappings in the service contract.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' X ', 'units': 2, 'price_cents': 30}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 60
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'x', 'sum_revenue_cents': 60}]
```
