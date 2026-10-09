# Native row services

Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `window(rows, lookup, request)`, and `lookup(rows, lookup, request)` (the last function shares its name with its lookup-table argument). Each accepts a list of row dictionaries, a lookup list (ignored except by lookup service), and a request dictionary. Inputs are never mutated.

`fill` supports `zero`, `mean`, and `median` (default `zero`); missing units are filled from the input's nonmissing units and all-missing inputs fill with zero. Regions are stripped/lowercased when strings. Revenue is `units * price_cents`, or `None` when price is missing. Original row column order is preserved and derived columns appended.

`group` returns region plus `<agg>_revenue_cents`; `monthly` returns month, region and that aggregate. Both drop null grouping keys; `agg` is `sum`, `mean`, or `count` (default sum), with count restricted to nonmissing revenue. Empty means are `None`. Results sort by stringified keys. Lookup adds `revenue_cents_per_target`; lookup keys are exact against normalized row regions, with absent/zero/null targets producing `None`. Window adds a trailing ROWS mean including current; `window` is 2, 3, or 4 (default is required in request; no default is applied). No external dependencies.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
All outputs use native Python values; date month extraction uses the first seven characters of the date string.
