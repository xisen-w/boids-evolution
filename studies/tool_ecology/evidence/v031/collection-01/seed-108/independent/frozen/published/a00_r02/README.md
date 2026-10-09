# Row transforms

Native Python implementation of the clean, revenue, group, monthly, lookup, and window services. Import named functions from `candidate`; every function accepts `(rows, lookup, request)` and returns fresh dictionaries/lists without mutating inputs.

- `clean`: normalized stripped/lowercase region and filled units.
- `revenue`: filled units and `revenue_cents`, without changing region.
- `group`: normalized region; drops missing region and aggregates nonmissing revenue.
- `monthly`: adds `month` from the first seven date characters, groups by month and normalized region.
- `lookup`: normalized region and adds exact-key `revenue_cents_per_target` (duplicate lookup keys: last wins).
- `window`: revenue plus trailing ROWS mean in `roll_revenue_cents` (request window must be 2, 3, or 4); region is unchanged.

Fill is selected by `request['fill']` (`zero`, `mean`, `median`; default zero). All-missing units fill as zero. Aggregation uses `request['agg']` (`sum`, `mean`, `count`; default sum); empty means are None and empty sums/counts are zero. Example:

```python
from candidate import revenue
revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
