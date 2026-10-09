# Tabular service adapters

The package exports six functions. Every function takes `(rows, lookup, request)` and returns a newly built result without modifying inputs. `lookup` is used only by the lookup service.

```python
from candidate import clean, revenue, group, monthly, lookup, window
clean(rows, [], {'fill': 'median'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'count'})
lookup(rows, [{'region': 'west', 'target': 10, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 3})
```

Fill modes are `zero`, `mean`, and `median` (all-missing fills with zero); aggregations are `sum`, `mean`, and `count`. Regions are stripped and lowercased. Grouped services omit missing keys and sort keys lexically by their string representation. Lookup performs normalized exact region matching and does not append lookup metadata. Windows use trailing row positions including the current row. Revenue and all service output schemas follow the service contract. No extra schema validation is provided.
