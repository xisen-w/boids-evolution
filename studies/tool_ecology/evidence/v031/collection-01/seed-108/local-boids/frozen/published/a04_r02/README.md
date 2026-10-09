# Tabular service functions
Dependency-free functions accept `(rows, lookup, request)`, return new lists and do not mutate inputs.

- `clean`: normalize region strings with strip/lower and fill missing units using `request['fill']` (`zero`, `mean`, `median`; all-missing fills with zero). Keeps columns/order.
- `revenue`: fill units and append `revenue_cents` (None if units or price is None); original region is unchanged.
- `group`: normalized-region revenue grouped by nonmissing region, aggregation selected by `request['agg']` (`sum`, `mean`, `count`).
- `monthly`: adds YYYY-MM month and groups by nonmissing month and normalized region.
- `lookup`: normalized-region revenue plus ratio to exact normalized region target; unknown, missing/zero target or missing revenue gives None.
- `window`: revenue plus mean of nonmissing revenue in trailing `request['window']` rows including current (2, 3, or 4); missing values do not extend the row window.

Grouped output columns are keys followed by `<agg>_revenue_cents`; stringified keys determine sorting. Sum/count on an all-null encountered group are zero; mean is None. Empty input produces empty grouped output. Invalid fill/aggregation/window raises ValueError.

Example:
```python
from candidate import revenue, group
rows = [{'region':' EAST ', 'units':None, 'price_cents':10}]
revenue(rows, [], {'fill':'zero'})
# [{'region':' EAST ', 'units':0, 'price_cents':10, 'revenue_cents':0}]
group(rows, [], {'fill':'zero', 'agg':'sum'})
# [{'region':'east', 'sum_revenue_cents':0}]
```
