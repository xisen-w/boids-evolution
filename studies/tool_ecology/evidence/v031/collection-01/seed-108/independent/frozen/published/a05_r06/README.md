# Row service transformations

A dependency-free native Python package implementing the six row-table service families. Public functions all have the signature `(rows, lookup, request)` and return new lists/dictionaries; input objects are not mutated.

```python
from candidate import clean, revenue, group, monthly, lookup as add_lookup, window
rows = [{'region': ' West ', 'units': None, 'price_cents': 125, 'date': '2025-03-04'}]
request = {'fill': 'zero', 'agg': 'sum', 'window': 3}
cleaned = clean(rows, [], request)  # [{'region': 'west', 'units': 0, ...}]
priced = revenue(rows, [], request) # adds revenue_cents (0)
by_region = group(rows, [], request) # [{'region': 'west', 'sum_revenue_cents': 0}]
by_month = monthly(rows, [], request)
per_target = add_lookup(rows, [{'region':'west','target':2,'manager':'M'}], request)
rolling = window(rows, [], request)
```

`clean` normalizes region with strip/lower and fills missing units. `revenue` fills units and derives `revenue_cents`; it deliberately preserves region as given. Group and monthly normalize region, derive revenue, omit missing group keys, and aggregate nonmissing values. `lookup` normalizes region and adds per-target revenue without adding lookup fields. `window` derives revenue and a trailing ROWS mean, preserving region. Fill modes are `zero`, `mean`, and `median` (all missing -> zero; even median averages the middle pair). Aggregations are `sum`, `mean`, and `count` (count means nonmissing revenue); window sizes are 2, 3, or 4. Missing derived operands yield `None`; empty aggregate sums/counts are zero and empty means are `None`. Region groups are sorted by string representation; monthly keys are lexicographically sorted. Unknown lookup regions, missing/zero targets, and missing revenue produce a `None` ratio.

Inputs are expected to be lists of dictionaries following the service schema. Invalid fill, aggregate, or window values raise `ValueError`. The module does not validate schema types beyond these service cases; duplicate normalized lookup keys use the last lookup row.
