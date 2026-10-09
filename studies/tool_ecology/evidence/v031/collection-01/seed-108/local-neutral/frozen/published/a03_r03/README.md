# Row services

Pure-Python row-table transformations. Public functions `clean(rows, lookup=None, request=None)`, `revenue(rows, lookup=None, request=None)`, `group(rows, lookup=None, request=None)`, `monthly(rows, lookup=None, request=None)`, `lookup(rows, lookup, request=None)`, and `window(rows, lookup=None, request=None)` implement the respective service families. `*_service` names are equivalent thin service adapters, taking `(rows, lookup, request)`.

Inputs are lists of dictionaries; functions return fresh dictionaries/results and do not mutate inputs. Requests support `fill` (`zero`, `mean`, `median`, default `zero`), `agg` (`sum`, `mean`, `count`, default `sum`), and `window` (2, 3, or 4; default 2). Missing units fill globally (all missing -> 0). Revenue is units times price, or None if either is missing. Clean and grouped families normalize region using strip/lower. Groups drop missing keys and ignore missing revenues; empty sum/count are zero and empty mean is None. Monthly groups on YYYY-MM month and normalized region. Lookup normalizes row/lookup region keys and adds only revenue per target; unknown, missing/zero target and missing revenue yield None. Window is mean of nonmissing revenue in trailing rows including current.

Example:

```python
from candidate import revenue, lookup
rows = [{'region': 'West', 'units': 2, 'price_cents': 125}]
assert revenue(rows)[0]['revenue_cents'] == 250
assert lookup(rows, [{'region': ' west ', 'target': 2, 'manager': 'A'}])[0]['revenue_cents_per_target'] == 125
```

Dates should be ISO strings and numeric values numbers or None. Invalid fill/agg/window values raise ValueError. Existing column order is retained; derived columns are appended.
