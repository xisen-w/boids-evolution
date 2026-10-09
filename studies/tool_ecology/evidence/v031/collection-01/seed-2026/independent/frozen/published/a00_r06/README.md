# Tabular service adapters

Import any public callable from `candidate`; all functions have signature
`function(rows, lookup, request)` and return fresh lists/dictionaries without
mutating inputs. This package re-exports the implementation in the declared
`a00_r01` dependency.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-02',
         'units': None, 'price_cents': 250, 'cost_cents': 100}]
clean(rows, [], {'fill': 'zero'})
# region is 'west', units is 0
revenue(rows, [], {'fill': 'zero'}) # appends revenue_cents
```

`clean` strips/lowercases regions and fills missing units. `revenue` additionally
appends `revenue_cents`. `group` and `monthly` aggregate nonmissing revenue,
respectively by region and by month/region, omitting missing grouping keys.
`lookup` adds `revenue_cents_per_target` from exact region matches; unavailable,
zero targets and unavailable revenue produce None. `window` adds the trailing
ROWS mean of available revenue, including the current row.

Requests use `fill` = `zero`, `mean`, or `median`; all-missing units fill to
zero and even-sized medians average their central values. Aggregators use
`agg` = `sum`, `mean`, or `count`, where count counts nonmissing revenue.
Window size is given by `window` (2, 3, or 4). Grouped outputs are sorted by
stringified keys; empty sum/count groups resolve to zero, empty means to None.
Original row columns/order are retained and derived columns appended. Invalid
policies may raise `ValueError`. Input rows are a list of dicts; lookup rows
contain region and target. This adapter adds no behavior beyond its dependency.
