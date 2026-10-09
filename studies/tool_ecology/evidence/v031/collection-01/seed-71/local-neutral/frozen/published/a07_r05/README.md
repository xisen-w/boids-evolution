# a07_r05

Dependency-free native-Python row transforms. Each public adapter accepts `(rows, lookup, request)` and returns a new list of dictionaries without mutating inputs.

- `clean`: fill missing units (`fill`: `zero`, `mean`, `median`; default `zero`) and normalize region using strip/lower; preserves all columns and row order.
- `revenue`: fill units and append `revenue_cents`; missing operands produce `None`.
- `group`: normalized region groups; drops missing region; `agg` is `sum`, `mean`, or `count` (default `sum`), counting nonmissing revenue.
- `monthly`: additionally groups on `date[:7]`, dropping missing month/region.
- `lookup`: normalized exact region-key target lookup; appends only `revenue_cents_per_target`, `None` for missing revenue, unknown region or zero/missing target.
- `window`: appends trailing row-window mean of nonmissing revenue, with `window` selecting the trailing rows (default 2).

All-missing units fill to zero. Empty aggregate groups are absent. Example:

```python
from candidate import revenue
revenue([{'region': 'East', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': 'East', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Inputs are expected to use the documented row schema and numeric values; malformed values are not supported. Region normalization is applied only in clean/group/monthly/lookup, as specified.
