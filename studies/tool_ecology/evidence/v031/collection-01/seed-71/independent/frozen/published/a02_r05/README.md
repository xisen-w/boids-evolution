# Tabular service adapters

Native Python package offering six pure service adapters, each taking
`(rows, lookup, request)` and returning a new list without mutating inputs.
The second argument is the lookup table only for `lookup`; other adapters
ignore it.

```python
from candidate import clean, revenue, group, monthly, lookup, window

clean(rows, [], {'fill': 'median'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'count'})
lookup(rows, [{'region': 'west', 'target': 10, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 3})
```

Fill choices: `zero`, `mean`, `median`; aggregations: `sum`, `mean`,
`count`; window sizes: 2, 3, or 4. Region normalization is strip/lower.
Grouped results omit missing keys and are sorted by stringified keys;
lookup uses normalized exact region keys and emits no lookup metadata. Window
means use row positions in the trailing window, including current. Missing
values and output schemas follow the service contract. This package reuses
`published.a02_r04` and does not add input schema validation.
