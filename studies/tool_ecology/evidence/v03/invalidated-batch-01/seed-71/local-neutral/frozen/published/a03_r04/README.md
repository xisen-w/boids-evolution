# Row-table analytics adapters

This package re-exports the tested native Python implementations from `published.a03_r03`; it adds no transformation semantics of its own. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.

Rows are lists of dictionaries. Functions do not mutate input rows or request and return new dictionaries. `clean` normalizes region with strip/lower and fills missing units. `revenue` fills missing units and appends `revenue_cents`. `group` and `monthly` normalize region, derive revenue, and return aggregate records; monthly also groups by date prefix. `lookup` normalizes region, derives revenue and appends `revenue_cents_per_target` using exact normalized region matching (last duplicate lookup wins), without adding lookup metadata. `window` derives revenue and appends the trailing physical-row mean `roll_revenue_cents`.

Request options: `fill` is `zero`, `mean`, or `median` (default `zero`; all missing fills as zero; even median averages middle values); `agg` is `sum`, `mean`, or `count` (default `sum`, count excludes missing revenue); `window` is a positive integer (default 2). Missing revenue operands yield `None`; empty sum/count yield zero and empty mean yields `None`. Grouping drops missing keys. Inputs are expected to have numeric units/prices, string-or-None regions, and ISO-like dates; invalid fill/agg options and nonpositive window widths raise `ValueError`.

Example:
```python
from candidate import revenue
rows = [{'region': 'North', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
