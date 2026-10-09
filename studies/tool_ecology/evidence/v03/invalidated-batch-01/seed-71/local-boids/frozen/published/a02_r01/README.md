# rowservices

Native-Python transformations for the six row-table service families. All APIs accept `(rows, lookup, request)`; inputs are not mutated and each output row is a new dictionary. `clean` normalizes regions and fills missing units; `revenue` additionally derives `revenue_cents`; `group` and `monthly` aggregate that revenue; `lookup` adds revenue per normalized-region target; `window` adds trailing-row revenue mean. Fill choices are `zero`, `mean`, and `median` (all-missing units fill with zero); aggregation choices are `sum`, `mean`, and `count`. Groups exclude missing keys and count only nonmissing revenue. Window is 2, 3, or 4 rows, including the current row.

```python
from candidate import revenue, group, monthly, lookup, window, clean
rows = [{'region':' NW ', 'date':'2025-01-03', 'units':2,
         'price_cents':50, 'id':1, 'product':'x', 'cost_cents':20}]
request = {'fill':'median', 'agg':'sum', 'window':2}
revenue_rows = revenue(rows, [], request)  # region='nw', revenue_cents=100
summary = group(rows, [], request)        # [{'region':'nw','sum_revenue_cents':100}]
```

Rows should use the documented fields; absent optional values are treated as missing where relevant. Lookup region matching uses stripped, lowercase region keys. Unknown or zero targets yield `None`. Invalid fill/agg/window values raise `ValueError`.
