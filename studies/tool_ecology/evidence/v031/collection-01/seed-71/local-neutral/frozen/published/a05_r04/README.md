# Table service adapters

Public API: `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each takes the three specified arguments and returns a newly transformed list of dictionaries. Inputs are not mutated. Only `lookup` uses lookup records.

```python
from candidate import revenue, monthly
rows = [{'region': ' West ', 'date': '2025-01-03', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})
monthly(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

`clean` normalizes region by strip/lower and fills missing units. Revenue fills units, then derives `revenue_cents`, None if either operand is missing. Group/monthly aggregate nonmissing revenue by sum/mean/count and drop missing keys. Lookup uses exact normalized region keys and adds per-target revenue; unknown regions, missing/zero targets, or missing revenue give None. Window computes trailing ROWS mean over nonmissing revenue, including current row. Fill options are zero/mean/median (even median averages middle pair; all missing fills zero); window sizes are 2/3/4. Functions expect the documented row/request schema and do not promise validation for malformed inputs.
