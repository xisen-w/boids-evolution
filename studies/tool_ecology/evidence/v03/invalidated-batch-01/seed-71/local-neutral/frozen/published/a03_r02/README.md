# Row analytics

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. All return fresh dictionaries and leave inputs untouched. `lookup` is an input list for the lookup service.

All row services retain source fields and order. Region values are stripped and lowercased. Missing units are filled from nonmissing units according to `request['fill']` (`zero`, `mean`, or `median`, default `zero`); all-missing fills with zero. Revenue is units times price, or None if either is missing. Group and monthly aggregate nonmissing revenue using `request['agg']` (`sum`, `mean`, `count`, default `sum`), exclude missing keys, and sort stringified keys. Monthly derives the first seven date characters. Lookup adds `revenue_cents_per_target`; unknown/missing/zero targets and missing revenue result in None. Window adds `roll_revenue_cents`, the nonmissing mean within trailing physical rows including current; `request['window']` is 2, 3, or 4 (default 2).

Example:

```python
from candidate import revenue, group
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
assert revenue(rows, [], {})[0]['revenue_cents'] == 100
assert group(rows, [], {'agg':'sum'}) == [{'region':'west','sum_revenue_cents':100}]
```

Expected inputs are lists of dictionaries with the service fields; arithmetic values should be numeric and dates strings. Invalid fill, aggregation, or window choices raise ValueError.
