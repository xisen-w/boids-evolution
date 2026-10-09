# Native tabular services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns fresh row dictionaries or aggregate dictionaries and does not modify inputs. `clean` normalizes region and fills missing units; `revenue` additionally derives `revenue_cents`; `group` and `monthly` aggregate that revenue, using request `agg` (`sum`, `mean`, `count`); `lookup` adds revenue divided by the normalized region's lookup target; `window` adds trailing-row revenue means.

Fill defaults to `zero` and accepts `zero`, `mean`, or `median`; mean/median use observed units and all-missing resolves to zero. Aggregation defaults to `sum`; empty means are `None`. Window defaults to 2 and accepts 2, 3, or 4. Example:

```python
from candidate import group
rows = [{'region':' North ', 'units':2, 'price_cents':50}]
assert group(rows, [], {'fill':'zero','agg':'sum'}) == [{'region':'north','sum_revenue_cents':100}]
```

Limitations: input rows are expected to be mappings with the service schema; invalid fill/aggregation/window values raise `ValueError`. Lookup regions are normalized with the same strip/lower rule; duplicate normalized lookup keys use the last entry.
