# tabular services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes a list of row dictionaries, a lookup-row list (unused except by `lookup`), and a request dictionary; inputs are not mutated. Row-preserving outputs are fresh dictionaries preserving input key order, with derived fields appended.

`fill` accepts `zero`, `mean`, or `median` (all missing means zero); aggregations accept `sum`, `mean`, or `count`. Grouped functions omit null keys and sort keys. Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Region strings are stripped and lowercased. Lookup region keys are normalized by the same rule. Window is trailing row count including current; null revenues do not contribute. Assumes valid request options and input schemas described by the service contract.
