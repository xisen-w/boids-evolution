# Tabular service adapters

Exports six callables, each accepting `(rows, lookup, request)` and returning fresh row dictionaries or grouped dictionaries without mutating inputs: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. They delegate to the verified native implementation in `published.a06_r02` (declared dependency).

`request.fill` is `zero`, `mean`, or `median`; all-missing units fill with zero. `request.agg` is `sum`, `mean`, or `count`. `request.window` selects trailing ROWS for the rolling mean. Examples:

```python
from candidate import revenue, group
revenue([{'region':' North ', 'units':None, 'price_cents':50}], [], {'fill':'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 50, 'revenue_cents': 0}]
group([{'region':' North ', 'units':2, 'price_cents':50}], [], {'fill':'zero','agg':'sum'})
# [{'region': 'north', 'sum_revenue_cents': 100}]
```

Schemas are mapping rows with required service fields; malformed non-mapping records are unsupported. Revenue and window preserve the region as specified; clean/group/monthly/lookup normalize it.
