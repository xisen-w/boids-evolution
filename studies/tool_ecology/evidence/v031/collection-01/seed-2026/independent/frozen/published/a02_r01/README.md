# Tabular services

Native Python implementation of the six row-table service families. Public functions all accept `(rows, lookup, request)` and return new lists/dictionaries without mutating input data. Rows retain their original keys and order; derived columns are appended.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' North ', 'date': '2025-01-02', 'units': None,
         'price_cents': 5, 'id': 1, 'product': 'x', 'cost_cents': 2}]
cleaned = clean(rows, [], {'fill': 'zero'})
assert cleaned[0]['region'] == 'north' and cleaned[0]['units'] == 0
priced = revenue(rows, [], {'fill': 'zero'})
assert priced[0]['revenue_cents'] == 0
```

`clean` supports `zero`, `mean`, and `median` unit fill (all missing fills with zero). `revenue` appends `revenue_cents`, null when price or filled units is null. `group` and `monthly` aggregate non-null revenue with `sum`, `mean`, or `count`; their output is sorted by keys and missing grouping keys are excluded. `lookup` appends revenue divided by the matching normalized region's target, or null for missing/zero target or missing revenue. `window` appends the mean of non-null revenue in the trailing requested number of rows including current. Defaults are zero fill, sum aggregation, and window 2. Lookup manager and other lookup fields are not added. Region normalization applies strip/lower to strings.
