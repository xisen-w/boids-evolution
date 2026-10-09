# Tabular services

Dependency-free Python implementations. Public adapters accept `(rows, lookup, request)` and return new list/dict values without mutating inputs. `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement the corresponding service contracts. Requests use `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), or `window` (trailing row count). Missing numeric values are `None`; all-missing units fill as zero. Group means with no nonmissing revenues are `None`.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'}) # revenue_cents=100; region unchanged
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

`clean` normalizes region but does not derive revenue; `revenue` and `window` preserve region as supplied. Grouping/lookup services normalize string regions with strip/lower. No validation of malformed dates or request enumerations is provided.
