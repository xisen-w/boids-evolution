# Row services

Import the top-level functions from `candidate`. Every service has the API
`function(rows, lookup, request)`, accepts a list of dictionaries, and returns
new dictionaries without modifying its inputs. `clean`, `revenue`, `group`,
`monthly`, `lookup_rate`, and `window` implement the corresponding service
families. Root service-check adapters are `clean_service`, `revenue_service`,
`group_service`, `monthly_service`, `lookup_service`, and `window_service`.

Example:
```python
from candidate import group
rows = [{'region': ' West ', 'units': None, 'price_cents': 20}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 0}]
```

Fill options are `zero`, `mean`, and `median` (empty input values fill with
zero); aggregations are `sum`, `mean`, and `count`. Window size comes from
`request['window']` and uses physical trailing rows. Lookup matches normalized
region keys. The functions assume valid service parameter values and numeric
operands; they do not validate malformed records or dates.
