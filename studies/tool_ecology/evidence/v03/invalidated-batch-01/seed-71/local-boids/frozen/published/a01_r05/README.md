# Sales table service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
Each accepts a list of row dictionaries, a lookup table (or `[]` when unused),
and a request dictionary; each returns its family's complete transformed output.
Inputs are not mutated. Example:

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'date': '2025-01-02', 'units': None,
         'price_cents': 10}]
clean(rows, [], {'fill': 'zero'})
revenue(rows, [], {'fill': 'mean'})
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
monthly(rows, [], {'fill': 'zero', 'agg': 'mean'})
lookup(rows, [{'region': 'west', 'target': 2, 'manager': 'A'}], {'fill': 'zero'})
window(rows, [], {'fill': 'zero', 'window': 2})
```

Fill accepts `zero`, `mean`, or `median` (all-missing becomes zero; even median
averages the middle pair). Regions are stripped/lowercased. Aggregation accepts
`sum`, `mean`, or `count`; count includes nonmissing revenues. Grouping drops
missing keys; monthly groups by `date[:7]` and region. Lookup adds only the
per-target revenue field, using normalized exact region keys. Window uses a
trailing number of rows including current, not a count of nonmissing rows.
Row-wise operations preserve original columns/order and append derived values;
grouped results sort by stringified keys. This API follows the service input
schema and is not a general dataframe library. Implementation is backed by
`published.a01_r04`.
