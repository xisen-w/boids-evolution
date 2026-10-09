# Row-table services

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` accept lists
of row dictionaries, lookup dictionaries, and a request dictionary. They return
fresh results and do not mutate inputs. This package re-exports the corresponding
verified implementations from `published.a01_r04`.

`clean` normalizes non-null regions with strip/lower and fills null units using
`request['fill']` (`zero`, `mean`, or `median`; all-missing becomes zero).
`revenue` additionally derives `revenue_cents`, null if either operand is null.
`group` aggregates by normalized region and `monthly` by month and region;
both drop missing grouping keys and accept `request['agg']` (`sum`, `mean`,
`count`). `lookup` adds `revenue_cents_per_target` from exact normalized region
lookup; unknown/missing/zero targets produce null. `window` adds the trailing
`request['window']`-row non-null revenue mean. Example:

```python
from candidate import clean
clean([{'region': ' NW ', 'units': None}], [], {'fill': 'zero'})
# [{'region': 'nw', 'units': 0}]
```

Inputs and request values must follow the service schema and supported choices.
