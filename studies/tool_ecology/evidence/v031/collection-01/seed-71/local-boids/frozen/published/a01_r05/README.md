# Row services

Provides six functions with the common signature `(rows, lookup, request)`, each
returning a new list of dictionaries and leaving inputs unchanged:

* `clean`: normalize region by strip/lower and fill missing units.
* `revenue`: clean plus `revenue_cents`.
* `group`: aggregate revenue by normalized region.
* `monthly`: aggregate by month and normalized region.
* `lookup`: attach revenue per region target.
* `window`: attach trailing row-window revenue mean.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}]
```

Fill modes are `zero`, `mean`, and `median` (even medians average the center
values); aggregation modes are `sum`, `mean`, and `count`. Window size is
provided by `request.window`. Missing values, output schemas, grouping/sorting,
and valid parameter behavior follow the declared service contract. Invalid
modes and malformed input rows are not promised to be handled. Implementation
delegates to received `published.a04_r02`.
