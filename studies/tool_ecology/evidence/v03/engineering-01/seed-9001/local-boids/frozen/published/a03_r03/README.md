# Table services

Native Python functions accept `(rows, lookup, request)` and return new dictionaries; inputs are not mutated. Public functions: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`. Missing-unit fill is selected by `request['fill']` (`zero`, `mean`, `median`; default `zero`; all missing becomes zero). Aggregation is selected by `request['agg']` (`sum`, `mean`, `count`; default `sum`). Window width is `request['window']` (2, 3, or 4; default 2).

`clean` normalizes region and fills units. `revenue` fills units and adds revenue, preserving region. `group` and `monthly` normalize region, aggregate nonmissing revenue, and omit missing group keys. `lookup` normalizes row regions and adds revenue per matching normalized lookup region's target, omitting target and manager. `window` adds trailing-row mean revenue. All preserve original row key order and append derived keys. Empty means and undefined revenue are `None`; empty sum/count are zero.

```python
from candidate import clean, revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 4}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 4}]
revenue(rows, [], {})[0]['revenue_cents']  # 0
```

Inputs are expected to follow the documented numeric/table contract. Invalid fill, aggregation, or window modes raise `ValueError`.
