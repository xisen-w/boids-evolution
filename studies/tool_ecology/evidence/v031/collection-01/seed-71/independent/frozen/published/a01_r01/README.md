# Tabular service adapters

Native Python implementation of the `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` service families. Public call signature for each is `(rows, lookup, request)`; rows and lookup are lists of dictionaries and request is a dictionary. Inputs are copied and never mutated.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' North ', 'date': '2025-01-10', 'units': None,
         'price_cents': 25}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'north', 'date': '2025-01-10', 'units': 0, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 0
```

`fill` is `zero`, `mean`, or `median`; missing units use zero if all units are missing. `agg` is `sum`, `mean`, or `count`; aggregations ignore missing revenue (empty means are None). `window` accepts 2, 3, or 4 rows. Region strings are stripped and lowercased. Group services omit missing grouping keys. Lookup normalizes lookup regions as well as row regions and returns None for unknown, zero, or missing targets. Derived columns are appended; original fields and order are otherwise retained. Dates are expected in ISO `YYYY-MM-DD` form. Unknown fill/aggregation modes and unsupported window sizes raise ValueError.
