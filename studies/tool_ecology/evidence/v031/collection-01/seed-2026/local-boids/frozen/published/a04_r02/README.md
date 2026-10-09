# Tabular service adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each accepts `(rows, lookup, request)` and returns new dictionaries/lists without mutating inputs. `clean` normalizes non-null string regions (strip/lower) and fills missing units. `revenue` fills units and appends `revenue_cents` without changing region. `group` and `monthly` normalize regions and return grouped aggregates, dropping missing keys; `lookup` normalizes regions and appends `revenue_cents_per_target`; `window` appends `roll_revenue_cents`.

`request['fill']` accepts `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero, and even medians average the central pair. Grouping uses `request['agg']` (`sum`, `mean`, `count`; default `sum`) and excludes missing revenues. Empty group sum/count are zero; mean is None. `window` uses `request['window']` 2, 3, or 4 (default 2) trailing rows including current. Lookup matches normalized region exactly; unknown, missing/zero targets and missing revenue produce None. Only region/target are used from lookup; manager is not added.

Example:
```python
from candidate import revenue
revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
