# Tabular service adapters

This package exposes six non-mutating table service functions, each accepting
`(rows, lookup, request)` and returning new list/dict records. It reuses the
verified native implementation in `published.a01_r01` rather than duplicating
its service logic.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None, 'price_cents': 10}]
clean(rows, [], {'fill': 'zero'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'mean'})
lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 2})
```

Fill modes are `zero`, `mean`, and `median` (all-missing units fill as zero);
aggregations are `sum`, `mean`, and `count`; windows use trailing row counts
including the current record. Region keys are stripped/lowercased. Lookup's
manager is not added to outputs. See the dependency's documented behavior for
full semantics. This package requires `published.a01_r01` to be available.
