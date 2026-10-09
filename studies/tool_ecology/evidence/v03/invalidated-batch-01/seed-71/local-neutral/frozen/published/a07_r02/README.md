# Row services

Native Python package exposing `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns new row dictionaries and leaves inputs unchanged. The `lookup` argument is used only by the lookup service.

`clean` normalizes region by stripping and lowercasing and fills missing units. `revenue` fills missing units and adds `revenue_cents`; unlike clean it preserves region unchanged. Revenue is `None` if units or price is missing. Both support request `fill` of `zero`, `mean`, or `median` (default zero); all-missing units fill with zero. Median for even counts is the average of the middle values.

`group` and `monthly` normalize region and aggregate nonmissing revenue using request `agg` (`sum`, `mean`, or `count`, default `sum`). Missing group keys are omitted; empty sums/counts are zero and empty means are `None`. Monthly derives the `YYYY-MM` prefix from date, or None. `lookup` normalizes regions in rows and lookup keys and adds `revenue_cents_per_target`; unknown, missing, or zero targets and missing revenue produce None. `window` adds the mean revenue in trailing request `window` rows (2, 3, or 4), ignoring missing revenue but retaining row positions in the window.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 150}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'region': ' West ', 'units': 2, 'price_cents': 150, 'revenue_cents': 300}
]
```

Aggregations and cleaning reuse the verified `published.a07_r01` implementation. Invalid modes raise `ValueError`; ordinary numeric input types are expected.
