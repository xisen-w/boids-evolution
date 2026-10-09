# Table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Each has the signature `(rows, lookup, request)` where rows and lookup are lists of dictionaries and request is a dictionary. Calls return new row dictionaries and do not mutate inputs.

`clean` normalizes region by stripping whitespace and lowercasing, and imputes missing units. `revenue` imputes units and appends `revenue_cents` without changing region. `group` and `monthly` normalize region and aggregate nonmissing revenue, excluding missing grouping keys. `lookup` normalizes row regions, adds revenue per target from region-key targets, and does not add lookup fields. `window` appends the trailing row-window mean of nonmissing revenues.

Use `request.fill` = `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. Grouping uses `request.agg` = `sum`, `mean`, or `count` (default `sum`); means of empty values are `None`, while empty sum/count are zero. Window width is selected by `request.window` (2, 3, or 4; default 2). Example:

```python
from candidate import revenue, group
rows = [{'region': ' WEST ', 'units': None, 'price_cents': 5}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' WEST ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

The APIs assume the documented numeric input contract; invalid modes raise `ValueError`.
