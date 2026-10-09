# Row transforms

Dependency-free functions accepting `(rows, lookup, request)`; inputs are not modified. `rows` and lookup are lists of dictionaries. Results are newly allocated dictionaries/lists.

Root APIs `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window` implement the corresponding service transformations. `request.fill` is `zero`, `mean`, or `median` (even median averages the middle values; empty/all-null units fill as zero). Group requests additionally require `agg` in `sum`, `mean`, `count`. Window requests require `window` in 2, 3, 4. Region strings are stripped/lowercased; null regions stay null. Revenue is units times price, or null if either is null. Group/monthly omit null grouping keys; means on empty groups are null. Lookup divides by exact normalized region target; null/zero/missing targets produce null. Window means cover trailing rows including current, ignoring null revenues.

Example:
```python
from candidate import revenue, group
rows = [{'region':' West ', 'units':2, 'price_cents':125}]
revenue(rows, [], {'fill':'zero'})[0]['revenue_cents']  # 250
# group(rows, [], {'fill':'zero', 'agg':'sum'})
```

Required fields are expected to have the documented scalar types; malformed dates, nonnumeric operands, and invalid request options are not coerced and can raise ordinary Python exceptions.
