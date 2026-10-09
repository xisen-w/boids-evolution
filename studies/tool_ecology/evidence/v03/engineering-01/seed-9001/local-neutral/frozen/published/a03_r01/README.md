# Row services

Native Python, no third-party dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. They return new lists/dictionaries and do not mutate inputs. `lookup` is the lookup-family adapter; its second argument is the lookup table.

All adapters expect request `fill` equal to `zero`, `mean`, or `median`. Revenue-derived functions fill missing units before calculating revenue; a missing price yields missing revenue. `group` and `monthly` also require `agg` equal to `sum`, `mean`, or `count`; `window` requires `window` equal to 2, 3, or 4. Regions are stripped and lowercased. For example:

```python
from candidate import group
rows = [{'region':' NORTH ', 'units':2, 'price_cents':50}]
group(rows, [], {'fill':'zero', 'agg':'sum'})
# [{'region': 'north', 'sum_revenue_cents': 100}]
```

Group outputs omit missing keys; aggregate functions ignore missing revenue. Lookup uses exact normalized region keys from the lookup table and adds only `revenue_cents_per_target`. Window means are over the trailing number of rows, including current, ignoring missing revenues. Inputs are assumed to follow the documented row schema and valid parameter values.
