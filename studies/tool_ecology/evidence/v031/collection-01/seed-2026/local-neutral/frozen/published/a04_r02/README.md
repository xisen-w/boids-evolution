# Row publication utilities

Native Python adapters for the six service families. Public call convention is
`family(rows, lookup, request)`; `rows` and `lookup` are lists of mappings and
`request` is a mapping. Functions return new lists and do not mutate inputs.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region':' NORTH ', 'date':'2025-01-03', 'units':None,
         'price_cents':250, 'id':1, 'product':'x', 'cost_cents':100}]
request = {'fill':'zero', 'agg':'sum', 'window':2}
cleaned = clean(rows, [], request)       # region 'north', units 0
extended = revenue(rows, [], request)    # also revenue_cents 0
```

`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement the
matching family semantics. Fill supports zero/mean/median (including even
median and all-missing fallback); aggregation supports sum/mean/count. Group
outputs omit missing keys and order keys lexically by their string form.
Window means cover trailing physical rows, including the current row. Lookup
expects exact keys in lookup rows; lookup region values are used as given.
Invalid fill, aggregation, or window parameters raise `ValueError`.
