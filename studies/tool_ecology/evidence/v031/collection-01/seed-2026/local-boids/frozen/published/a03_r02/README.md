# Row-table services

Native Python adapters for the recurring table services. Each adapter accepts
`(rows, lookup, request)` and returns new dictionaries without modifying inputs.

```python
from candidate import clean, revenue, group, monthly, lookup_service, window
clean(rows, [], {'fill': 'median'})
lookup_service(rows, [{'region': 'west', 'target': 10}], {'fill': 'zero'})
```

`clean`, `revenue`, `group`, `monthly`, and `window` delegate to the tested
`published.a00_r01` package. Aggregations ignore missing revenue; missing group
keys are dropped. Lookup region strings on both sides are stripped/lowercased;
unknown/zero/missing targets and missing revenue yield a null ratio. Inputs are
expected to conform to the service schema (including numeric values).
