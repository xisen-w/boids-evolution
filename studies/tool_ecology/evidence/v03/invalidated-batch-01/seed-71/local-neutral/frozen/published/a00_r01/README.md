# Tabular service utilities

Native Python, no third-party dependencies. Public adapters accept `(rows, lookup, request)` and return new dictionaries/lists without mutating their inputs. Rows retain input order for row-oriented families. Region strings are stripped and lowercased; non-string/missing regions are unchanged.

Adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

```python
from candidate import revenue, group
rows = [{'region':' West ', 'units':2, 'price_cents':30}]
revenue(rows, [], {'fill':'zero'})
# [{'region': 'west', 'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
group(rows, [], {'fill':'zero', 'agg':'sum'})
# [{'region': 'west', 'sum_revenue_cents': 60}]
```

`fill` is `zero`, `mean`, or `median`; missing units use the selected statistic (all-missing gives zero). Revenue is `None` when units or price is missing. Aggregation is `sum`, `mean`, or `count`; count counts nonmissing revenues. Missing group keys are excluded. `monthly` uses the first seven date characters and excludes missing month/region. `lookup` adds a per-target value, matching normalized region keys; absent, null, or zero targets produce `None`. `window` computes a trailing row window (including current row), width 2/3/4, averaging nonmissing revenues. Inputs are expected to be mappings with the documented fields; malformed values/unknown parameter names are not coerced.
