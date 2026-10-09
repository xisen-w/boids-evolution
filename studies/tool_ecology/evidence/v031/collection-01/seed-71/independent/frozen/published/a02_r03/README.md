# Tabular service adapters

Native Python adapters for the six tabular service families. Every function accepts
`(rows, lookup, request)` and returns the corresponding transformed list. The
`lookup` family interprets its second argument as the lookup table; other families
ignore that argument. Inputs are passed to the underlying implementation without
adapter-side mutation.

```python
from candidate import clean, revenue, group, monthly, lookup, window
clean(rows, [], {'fill': 'median'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'count'})
lookup(rows, [{'region': 'west', 'target': 10, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 3})
```

`fill` is `zero`, `mean`, or `median`; grouped `agg` is `sum`, `mean`, or
`count`; trailing window size is 2, 3, or 4. The underlying API normalizes
region keys as specified, drops missing group keys, and handles missing numeric
values per the service contract. Lookup is exact on normalized region and does
not emit lookup metadata. Window means use trailing row positions, including the
current row. Inputs are expected to follow the service schema; this adapter adds
no validation or coercion beyond the underlying API. Implementation is reused
from received package `a02_r02`.
