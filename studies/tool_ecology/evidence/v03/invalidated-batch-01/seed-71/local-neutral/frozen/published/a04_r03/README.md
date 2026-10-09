# Row services

Dependency-backed native Python adapters for six table transformations. Import any of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`; each has signature `(rows, lookup, request)` and returns a new list of dictionaries without mutating its inputs.

Example:
```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 25}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
```

`fill` is `zero`, `mean`, or `median` (even medians average central values; all missing fills with zero). `agg` is `sum`, `mean`, or `count`; groups discard missing keys and missing revenues. `window` uses trailing rows including the current row and accepts 2, 3, or 4. Clean, grouping, monthly, and lookup normalize regions by strip/lower; revenue and window preserve region values. Lookup ratios use normalized exact region keys. Original row fields are preserved for row-oriented outputs; grouping outputs contain only keys and aggregate. Inputs are expected to follow the documented service schema; malformed dates and unsupported options raise errors or are not specially handled.
