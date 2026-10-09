# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each accepts `(rows, lookup, request)` where rows/lookup are lists of dictionaries and request is a dictionary. Inputs are not mutated; results are newly-created dictionaries.

```python
from candidate import revenue, window
rows = [{'region': ' North ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```

`fill` accepts `zero`, `mean`, or `median` (all missing units fill with zero). Clean normalizes region strings by stripping/lowercasing. Revenue and window preserve the input region unchanged; group, monthly, and lookup normalize it. Revenue is None if price or filled units is None. Aggregation `agg` is `sum`, `mean`, or `count`; missing revenues are ignored, with empty mean None. Groups omit missing keys and sort lexicographically by stringified keys. Monthly uses the first seven date characters and omits missing dates. Lookup normalizes lookup keys, adds only revenue per target (not target/manager), and gives None for missing/zero target, unknown region, or missing revenue. Window accepts widths 2, 3, or 4 and computes trailing-row mean over nonmissing revenues. Unknown fill/agg modes and unsupported window sizes raise ValueError. Dates are expected as ISO strings.
