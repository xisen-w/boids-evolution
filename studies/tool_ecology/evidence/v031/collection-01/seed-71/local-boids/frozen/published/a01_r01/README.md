# tabular-services

A dependency-free Python package implementing six row-table services. Public adapters all have signature `(rows, lookup, request)` and return new dictionaries/lists; inputs are not mutated. Missing values are represented by `None`.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' North ', 'date': '2025-01-03', 'units': 2,
         'price_cents': 150}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'north', 'date': '2025-01-03', 'units': 2, 'price_cents': 150}]
revenue(rows, [], {'fill': 'zero'})  # adds revenue_cents=300
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

`clean` normalizes region and fills missing units, preserving input fields. `revenue` also adds `revenue_cents`. `group` aggregates nonmissing revenue by nonmissing region; `monthly` groups by month and region. `lookup` adds revenue divided by the exact normalized-region key's target (lookup keys are expected already normalized). `window` adds trailing row-window revenue means. Fill is `zero`, `mean`, or `median` (all missing becomes zero); aggregation is `sum`, `mean`, or `count`; window is 2, 3, or 4. Unknown parameter values raise `ValueError`. Aggregate empty mean is `None`; sum/count of empty values are zero. These functions expect valid row fields and numeric operands; they do not validate ISO dates beyond slicing the first seven characters.
