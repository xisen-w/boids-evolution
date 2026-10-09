# Tabular service API

This package exposes six pure, dependency-backed service functions. Every function
has the signature `function(rows, lookup, request)` and returns fresh row dictionaries
(or grouped result dictionaries); inputs are not mutated. The implementation is
re-exported from the received package `published.a00_r01` (declared dependency).

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-02',
         'units': None, 'price_cents': 250, 'cost_cents': 100}]
clean(rows, [], {'fill': 'zero'})  # region='west', units=0
revenue(rows, [], {'fill': 'zero'})  # revenue_cents=0; region stays ' West '
window(rows, [], {'fill': 'zero', 'window': 2})
```

`clean` normalizes region (strip/lower) and fills units. `revenue` fills units
and adds `revenue_cents`; grouping and lookup normalize region while window does
not. `group` aggregates on region and `monthly` on month plus region, excluding
missing grouping keys. Both emit `<agg>_revenue_cents`, with aggregation selected
by `request['agg']` (`sum`, `mean`, `count`). Count includes only nonmissing
revenue. Mean of no values is `None`; empty sum/count are zero. Group results sort
by stringified keys. `lookup` appends revenue per exact region-key target; unknown,
missing, or zero targets yield `None`. `window` appends the mean of nonmissing
revenue in the trailing `request['window']` rows, where valid widths are 2, 3, 4.

`request['fill']` accepts `zero`, `mean`, or `median`; all-missing units fill with
zero and even-length medians average the central values. Missing values are `None`.
Original columns and row order are preserved by row-level services, with derived
fields appended. Invalid fill/aggregation/window parameters raise `ValueError`.
