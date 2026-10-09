# Table transformation services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Every callable has signature `(rows, lookup_rows, request)` and returns a new list of dictionaries without mutating input. Implementations are delegated to `published.a07_r05`.

* `clean`: strip/lower region; fill missing units using request `fill` (`zero`, `mean`, `median`; all-missing becomes 0). Preserves columns and row order.
* `revenue`: clean behavior plus `revenue_cents = units * price_cents`, or `None` if either operand is missing.
* `group`: clean/revenue behavior, group by nonmissing region; `request.agg` is `sum`, `mean`, or `count` of nonmissing revenue. Output is sorted by stringified region.
* `monthly`: as group, grouped by month (`date[:7]`) and region, dropping missing keys, sorted by stringified keys.
* `lookup`: append `revenue_cents_per_target` using exact normalized region lookup. Unknown region, null/zero target, or null revenue gives `None`; lookup metadata is not appended.
* `window`: append trailing-row `roll_revenue_cents`, mean of nonmissing revenue in the window including current row; an empty window result is `None`.

Grouped outputs use columns `region` and `<agg>_revenue_cents`; monthly uses `month`, `region`, and the same aggregate column. Empty sum/count groups yield zero and empty mean yields `None`. Row services preserve original column order and append derived columns. Inputs are lists of dictionaries in the documented service schema; dates are expected to be ISO strings. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}
]
```
