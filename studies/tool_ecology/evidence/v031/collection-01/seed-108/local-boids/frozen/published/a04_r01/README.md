# Tabular services

Dependency-free Python APIs, each accepting `(rows, lookup, request)` and returning a new list of dictionaries without mutating arguments:

- `clean(rows, lookup, request)`: normalize string regions using strip/lower and fill missing `units` with `request['fill']` (`zero`, `mean`, or `median`; an all-missing column fills with zero). All columns and row order are retained.
- `revenue(...)`: clean behavior plus `revenue_cents = units * price_cents`, or `None` if either is missing.
- `group(...)`: revenue behavior grouped by normalized nonmissing region; `request['agg']` is `sum`, `mean`, or `count` of nonmissing revenue.
- `monthly(...)`: revenue behavior, month from the first seven date characters, grouped by month and region.
- `lookup(...)`: revenue behavior plus `revenue_cents_per_target`; target is matched on normalized exact region; absent/None/zero targets and missing revenue yield `None`.
- `window(...)`: revenue behavior plus mean revenue among nonmissing values in the trailing `request['window']` rows (2, 3, or 4), including the current row.

Aggregate outputs have only their specified grouping keys and `<agg>_revenue_cents`, sorted by stringified keys. Empty sum/count groups are not emitted; encountered all-null groups produce zero for sum/count and None for mean.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' EAST ', 'units': None, 'price_cents': 10}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': 'east', 'units': 0, 'price_cents': 10, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'east', 'sum_revenue_cents': 0}]
```

`rows` and `lookup` are expected to be sequences of mappings. Fill and aggregation names outside the documented choices raise `ValueError`; window sizes outside 2/3/4 raise `ValueError`.
