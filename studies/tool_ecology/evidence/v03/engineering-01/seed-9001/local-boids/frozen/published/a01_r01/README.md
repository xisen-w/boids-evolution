# rowservices

Pure-Python services for list-of-dictionary tables. Public adapters all have signature `(rows, lookup, request)`; inputs are not mutated. Columns are copied and derived columns appended. `clean` normalizes regions and fills units; `revenue` also derives revenue; `group` and `monthly` aggregate; `lookup` adds revenue per region target; `window` computes trailing row means.

Example:
```python
from candidate import revenue, group
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
revenue(rows, [], {'fill':'zero'})
# [{'region': 'west', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
group(rows, [], {'fill':'zero', 'agg':'sum'})
# [{'region': 'west', 'sum_revenue_cents': 100}]
```
Fill modes are zero/mean/median (all missing => zero); aggregate modes sum/mean/count. Revenue is None if a multiplicand is missing; aggregate mean is None for empty valid values. Lookup uses normalized region keys and returns None for absent/zero targets. Window averages nonmissing revenues in the positional trailing window. Extra keys in input rows are preserved. Invalid fill/agg/window values raise ValueError (or validation error).
