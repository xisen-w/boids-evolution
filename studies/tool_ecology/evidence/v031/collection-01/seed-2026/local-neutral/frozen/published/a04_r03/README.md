# Row service utilities

Pure native-Python implementations. Each public adapter takes `(rows, lookup, request)` and returns new dictionaries without modifying inputs. `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement corresponding service families. Request keys are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4); omitted options default to zero, sum, and no window respectively (window must be supplied to call it). All-missing units fill with zero; even medians average the two center values. Group outputs omit missing keys and sort lexically; means with no values are `None`, empty sum/count are zero. Region lookup is exact against normalized row region and provided lookup keys.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows=[{'region':' NORTH ', 'units':None, 'price_cents':20, 'date':'2025-01-03'}]
req={'fill':'zero','agg':'sum','window':2}
clean(rows, [], req)    # region north, units 0
revenue(rows, [], req)  # adds revenue_cents: 0
```
