# Row-table services

Native Python implementation, no third-party dependencies. Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` each take a list of dictionaries plus lookup rows and request dictionary. The six `*_service` names are equivalent top-level service adapters. Inputs are not mutated.

`clean` normalizes region by strip/lower and fills null units; `revenue` fills units and adds `revenue_cents`; `group` normalizes region and aggregates revenue by region; `monthly` aggregates by month and normalized region; `lookup` normalizes region and adds revenue per target; `window` adds trailing row-window revenue means. Fill modes are `zero`, `mean`, and `median` (empty non-null population fills with zero; even median averages the middle pair). Aggregate modes are `sum`, `mean`, and `count`; count excludes missing revenue. Window width is supplied in request as `window`.

Example:
```python
from candidate import group
result = group([{'region':' NW ', 'units':2, 'price_cents':50}], [], {'fill':'zero','agg':'sum'})
# [{'region': 'nw', 'sum_revenue_cents': 100}]
```

Results preserve source columns and row order for row-wise services; grouped results contain only group keys and aggregate. Null grouping keys are omitted. Revenue and window deliberately do not normalize region. Inputs are expected to have the service schema; aggregation and window modes must be supported values.
