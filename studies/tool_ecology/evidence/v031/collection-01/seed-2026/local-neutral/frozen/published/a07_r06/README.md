# Row table services

Native Python, no dependencies. Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` implement the six service contracts. Inputs are lists of dictionaries; functions return new dictionaries/lists and do not mutate inputs.

`clean` normalizes region strings using strip/lower and fills missing units (zero/mean/median; empty/all-missing uses zero). `revenue` additionally appends `revenue_cents` (None if units or price is missing). `group` and `monthly` return aggregate records using request `agg` (`sum`, `mean`, `count`), omitting missing group keys; monthly uses the first seven date characters. `lookup` appends `revenue_cents_per_target`, matching the normalized row region to lookup region keys. `window` appends the mean revenue over the trailing `request.window` rows including current.

Example:
```python
from candidate import revenue
rows = [{'region':' West ', 'units':2, 'price_cents':150}]
assert revenue(rows, [], {'fill':'mean'})[0]['revenue_cents'] == 300
```
Missing aggregates produce zero for sum/count and None for mean. Invalid fill, aggregation, or window values raise ValueError. Original columns retain their order and derived columns are appended.
