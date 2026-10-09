# rowservices

Pure-Python implementations of six row-table service families. Public functions accept `(rows, lookup, request)` and return new lists/dicts without mutating inputs. `request` is a mapping: `fill` is `zero`, `mean`, or `median` (default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 (default 2).

```python
from candidate import clean, group, window
cleaned = clean(rows, [], {'fill': 'median'})
summary = group(rows, [], {'fill': 'mean', 'agg': 'sum'})
rolling = window(rows, [], {'fill': 'zero', 'window': 3})
```

`clean` preserves columns/order while normalizing nonmissing regions with strip/lower and filling units; all-missing units become zero. `revenue` does the same and appends `revenue_cents`. `group` returns region plus `<agg>_revenue_cents`; `monthly` returns month, region and that aggregate. Both omit missing group keys; mean of no revenue is null and sum/count of no revenue is zero. `lookup` appends `revenue_cents_per_target`, using normalized exact region keys (unknown/zero/missing targets produce null). `window` appends the mean of nonmissing revenue in the trailing row window. Revenue is null if units or price is null. Aggregated results are sorted by stringified keys. Inputs are expected to be lists of dictionaries with the fields described by the service contract; malformed fields and unsupported parameters are not supported.
