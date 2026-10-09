# Tabular service facade

This package re-exports the tested native implementation in `published.a07_r02`;
it adds no alternate semantics and has no third-party dependencies. Inputs are
`rows`, `lookup`, and `request` (each a list of dictionaries / dictionary), and
are not mutated. Every function returns its complete family output.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2024-01-05', 'units': None,
         'price_cents': 20}]
clean(rows, [], {'fill': 'zero'})[0]['region']       # 'west'
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 0
```

Fill modes are `zero`, `mean`, `median` (all-missing means zero; even medians
average the middle values). Aggregations are `sum`, `mean`, or `count`; missing
revenue is excluded. Group and monthly omit missing keys. Lookup returns
`revenue_cents_per_target`, or `None` for unavailable/zero targets. Window
computes a trailing ROWS mean, including the current row, over nonmissing
revenue. The implementation follows the service schema and ISO date convention.
