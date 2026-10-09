# Pure Python row-table services

The package exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries and returns fresh output without mutating inputs. `lookup` is the region lookup-row list argument.

`clean` normalizes region with strip/lower and fills missing units; `revenue` fills units and appends revenue_cents. `group` and `monthly` aggregate nonmissing revenues by region, and by month/region respectively. `lookup` appends revenue_cents_per_target (exact normalized region match). `window` appends trailing physical-row mean roll_revenue_cents.

Request options: fill=`zero`, `mean`, or `median` (default zero; all missing fills zero); agg=`sum`, `mean`, or `count` (default sum); window is a positive integer (default 2). Group outputs drop missing keys and sort lexically. Empty sum/count results are zero; empty means are None. Lookup duplicate normalized regions use the last row. Dates are assumed ISO-like strings. Invalid option names raise ValueError. Existing row keys/order are preserved and derived columns appended.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {})[0]['revenue_cents'] == 100
assert group(rows, [], {'agg':'sum'}) == [{'region':'north','sum_revenue_cents':100}]
```
