# Row services

Pure-Python implementations of six row-table service families. Import the named functions from `candidate`; each accepts `(rows, lookup=None, request=None)` and returns fresh row dictionaries (or aggregate rows), without mutating inputs. `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` correspond to the service families.

Request keys: `fill` is `zero`, `mean`, or `median` (default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 (default 2). Missing units are filled across the input, with all-missing data filling to zero. Revenue is units times price, or `None` if either is missing. Region names are stripped and lowercased. Lookup keys are normalized the same way; unknown/missing/zero targets produce `None` and manager/target columns are not added. Aggregation ignores missing revenues. Grouping omits missing keys; mean of no values is `None`, sum/count are zero. Monthly uses the first seven date characters. Window means use trailing rows, including current, excluding missing revenues.

Example:

```python
from candidate import revenue, lookup
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows)[0]['revenue_cents'] == 250
assert lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}])[0]['revenue_cents_per_target'] == 125
```

Numeric columns are expected to contain numbers or `None`; dates should be ISO strings. Invalid fill/aggregation/window options raise `ValueError` (invalid fill is checked when filling is needed). Original column order is retained and derived columns appended.
