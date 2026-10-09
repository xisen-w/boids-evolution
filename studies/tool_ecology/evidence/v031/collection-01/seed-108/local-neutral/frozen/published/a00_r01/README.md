# Table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each has the exact signature `service(rows, lookup, request)` and returns a new list of dictionaries without mutating its inputs. `rows` is a list of row dictionaries, `lookup` is a list of region/target/manager dictionaries, and `request` supplies `fill` (`zero`, `mean`, or `median`) and, for aggregate services, `agg` (`sum`, `mean`, or `count`). `window` additionally takes `window` in 2, 3, 4. Example:

```python
from candidate import revenue
rows = [{'region':' West ', 'units':None, 'price_cents':25}]
print(revenue(rows, [], {'fill':'zero'}))
# [{'region': 'west', 'units': 0, 'price_cents': 25, 'revenue_cents': 0}]
```

`clean` preserves columns while normalizing region and filling units. `revenue` adds revenue; `group` and `monthly` aggregate it; `lookup` adds revenue per exact region target; `window` adds the trailing-row mean. Null regions/months are excluded from group outputs. Missing revenue is ignored by aggregates; empty sum/count are zero and empty mean is null. All-missing units fill with zero. Median uses the conventional midpoint for even-sized inputs. Dates are expected in ISO form. Unknown fill/aggregate options and unsupported window sizes raise `ValueError`.
