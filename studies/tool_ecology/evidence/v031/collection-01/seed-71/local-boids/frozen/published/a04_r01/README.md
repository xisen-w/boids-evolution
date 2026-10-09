# Row services

Native, dependency-free Python functions for the six row-table service families. All functions accept `(rows, lookup, request)`, return fresh dictionaries/lists, and do not mutate their arguments. Missing values are represented by `None`.

- `clean(rows, lookup, request)`: region strip/lower and units imputation only; preserves row/field order and fields.
- `revenue(...)`: same normalization/imputation plus `revenue_cents`.
- `group(...)`: returns grouped records with `region` and `<agg>_revenue_cents`.
- `monthly(...)`: returns records with `month`, `region`, and `<agg>_revenue_cents`.
- `lookup(...)`: appends `revenue_cents_per_target`; lookup region keys are normalized using strip/lower. Target and manager are not copied.
- `window(...)`: appends trailing-row `roll_revenue_cents`.

Request keys: `fill` is `zero`, `mean`, or `median` (default `zero`; all-missing -> 0); aggregate `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is a positive integer (default 2). Group aggregates ignore missing revenue; empty sum/count are zero and empty mean is `None`. Only `None` is treated as missing. Dates are assumed to be ISO strings. Example:

```python
from candidate import revenue, group
rows = [{'region': ' EAST ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': 'east', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'east', 'sum_revenue_cents': 100}]
```
