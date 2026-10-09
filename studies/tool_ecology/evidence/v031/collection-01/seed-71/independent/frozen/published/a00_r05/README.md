# Native tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are lists of dictionaries and a request dictionary; each returns newly allocated row dictionaries/results without mutating inputs.

Examples:

```python
from candidate import clean, group
clean(rows, [], {"fill": "median"})
group(rows, [], {"fill": "mean", "agg": "count"})
```

Fill choices are `zero`, `mean`, and `median` (even median averages the middle values; all missing fills to zero). Revenue is units times price, or `None` if price is missing. Group/monthly support `sum`, `mean`, and `count`; missing group keys are omitted and count counts nonmissing revenue. `monthly` derives YYYY-MM from the date string. Lookup matches normalized row region exactly against lookup region; unknown/missing/zero targets yield a `None` ratio and target/manager fields are not added. Window computes a trailing row-based mean, including current row, over widths 2, 3, or 4. Invalid options raise `ValueError`. No third-party dependencies.
