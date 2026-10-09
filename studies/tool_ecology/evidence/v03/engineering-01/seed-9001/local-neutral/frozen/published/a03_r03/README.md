# Table services

A small native-Python facade exposing six transformations on list-of-dict rows. Each public function has the exact signature `function(rows, lookup, request)`; `lookup` may be an empty list for services that do not need it. Functions return fresh outputs and delegate behavior to the received `published.a02_r01` implementation.

- `clean`: strip/lower non-null regions and fill missing units; preserves row shape/order.
- `revenue`: fill missing units and append `revenue_cents` (None if units or price is missing); region remains unchanged.
- `group`: normalized region and revenue, grouped by non-null region.
- `monthly`: normalized region/revenue, grouped by non-null month and region.
- `lookup`: normalized region/revenue and append revenue divided by exact-region target; unknown, missing/zero target, or missing revenue gives None.
- `window`: append trailing-row revenue mean including the current row.

`request.fill` is `zero`, `mean`, or `median` (default zero; all-missing fills zero; even median averages the two middle values). `request.agg` is `sum`, `mean`, or `count` (default sum; count excludes missing revenue). `request.window` selects trailing row width (default 2). Group outputs drop missing keys, sort lexically, and use zero for empty sum/count and None for empty mean. Inputs follow the service schema and valid request values; this facade does not add validation/coercion. Derived columns are appended and original row-wise column order is retained.

Example:

```python
from candidate import clean, revenue
rows = [{'region': ' EAST ', 'units': 2, 'price_cents': 50}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'east', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' EAST ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
