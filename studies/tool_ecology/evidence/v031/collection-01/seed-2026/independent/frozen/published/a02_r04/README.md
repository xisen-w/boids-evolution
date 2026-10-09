# Tabular service adapters

Dependency-free at the API boundary; implementations are reused from the verified `published.a02_r03` package. Each public function takes `(rows, lookup, request)` and returns a fresh list of dictionaries without mutating inputs:

* `clean`: normalize string regions with strip/lower and fill missing units.
* `revenue`: fill missing units and derive `revenue_cents`.
* `group`: normalize region, derive revenue, and aggregate by nonmissing region.
* `monthly`: normalize region, derive revenue, add YYYY-MM month, aggregate by nonmissing month/region.
* `lookup`: normalize region, derive revenue, and add `revenue_cents_per_target` from region-keyed lookup rows.
* `window`: derive revenue and add trailing-row `roll_revenue_cents`.

Fill requests use `{'fill': 'zero'|'mean'|'median'}` (default zero); all-missing units fill with zero, and even-sized median is the central-value average. Group requests use `{'agg': 'sum'|'mean'|'count'}` (default sum); count ignores missing revenue. Window requests use `{'window': 2|3|4}` (default 2), including current row. Mean aggregation/window over no values is `None`; empty sum/count groups are zero.

Example:
```python
from candidate import revenue, group
rows = [{'region': 'North', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 100
# [{'region': 'north', 'sum_revenue_cents': 100}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Unknown lookup regions, absent/zero targets, or absent revenue produce `None` per-target revenue. Revenue and window do not normalize region. Dates are treated as strings, using their first seven characters; malformed inputs and unsupported request values are not validated.
