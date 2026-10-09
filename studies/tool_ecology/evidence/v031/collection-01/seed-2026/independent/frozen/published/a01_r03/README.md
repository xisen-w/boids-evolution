# Tabular service adapters

This package exposes the native Python callables `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list of dictionaries and preserves input columns/order where appropriate; inputs are not mutated. It delegates to the received, dependency-declared package `published.a01_r02`.

- `clean`: strip/lower regions and fill missing units using request `fill` (`zero`, `mean`, or `median`; all missing gives zero).
- `revenue`: fill units and add `revenue_cents`; null if either operand is null. Region is not normalized.
- `group`: normalize region, derive revenue, drop missing region, and aggregate non-null revenue per request `agg` (`sum`, `mean`, `count`).
- `monthly`: as group, grouping on month (`date[:7]`) and region; missing keys are dropped.
- `lookup`: normalize region and add revenue per exact normalized region target; unknown, missing/zero target, or missing revenue gives null.
- `window`: add trailing `request['window']`-row mean of non-null revenue, including current row; region is not normalized.

Group outputs sort by stringified keys. Request parameters and input schema must be valid as specified by the service contract; dates are ISO strings. Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
req = {'fill': 'zero', 'agg': 'sum'}
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
assert group(rows, [], req) == [{'region': 'west', 'sum_revenue_cents': 0}]
```
