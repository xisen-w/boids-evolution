# Sales table transforms

Pure-Python adapters accept `(rows, lookup, request)` and return fresh dictionaries without modifying inputs. Public functions are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

- `clean`: strip/lower region strings and fill null units (`fill`: `zero`, `mean`, `median`; default `zero`; all-null becomes zero).
- `revenue`: fill units and append `revenue_cents`; null operands produce `None`.
- `group`: normalize regions, derive revenue, drop null region keys, aggregate non-null revenue (`agg`: `sum`, `mean`, `count`; default `sum`).
- `monthly`: as above, grouping by month from `date[:7]` and region; null keys are dropped.
- `lookup`: normalized exact region lookup and append revenue divided by target; missing/zero target or missing revenue gives `None`.
- `window`: derive revenue and append mean over nonmissing revenues in the trailing `window` rows including current (default 2).

Group outputs sort by stringified keys. Empty aggregate values yield zero for sum/count and `None` for mean. Example:

```python
from candidate import revenue
revenue([{'region': ' North ', 'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Inputs are expected to use the documented service schema and valid parameter values; dates are sliced as ISO `YYYY-MM-DD` without validation.
