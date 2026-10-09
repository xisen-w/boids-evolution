# Table services

Dependency-light public API: each function accepts `(rows, lookup, request)` and returns a fresh list of dictionaries (or grouped output). The `lookup` parameter is a list of lookup-table dictionaries; it is unused by all services other than `lookup`.

* `clean(rows, lookup, request)`: strip/lower non-null regions and fill null units.
* `revenue(...)`: fill units and derive `revenue_cents`; preserves region spelling.
* `group(...)`: normalize, derive revenue, then group by region.
* `monthly(...)`: normalize, derive revenue, then group by month and region.
* `lookup(...)`: normalize, derive revenue, and append `revenue_cents_per_target`; lookup region keys are normalized. Target and manager are not appended.
* `window(...)`: derive revenue, then append trailing ROWS mean `roll_revenue_cents`.

`request['fill']` accepts `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero. Group requests use `request['agg']` (`sum`, `mean`, or `count`; default `sum`); null group keys are excluded and missing revenues are excluded from aggregation. Empty sum/count are zero and empty mean is None. Window width is given by `request['window']` (default 2). Example:

```python
from candidate import group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}]
```

Inputs are expected to use the documented table fields and valid fill/aggregation choices. The implementation returns new row dictionaries and does not mutate input rows, lookup, or request. This package delegates to received implementation `a01_r02`.
