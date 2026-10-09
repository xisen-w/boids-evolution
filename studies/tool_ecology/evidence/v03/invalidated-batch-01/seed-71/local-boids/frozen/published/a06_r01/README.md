# tabular_services

Native Python adapters for the six recurring row-table services. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of dictionaries, lookup rows, and request dictionary and returns a new list without mutating inputs.

`fill` supports `zero`, `mean`, or `median` (all-missing units fill with zero); `agg` supports `sum`, `mean`, and `count`; window uses request `window` as trailing row count. Example:

```python
from candidate import revenue
revenue([{'region':' WEST ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})
# [{'region': 'west', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Revenue is `None` if either operand is missing. Grouping drops missing keys and excludes missing revenues from aggregates. Lookup uses exact keys against normalized row regions; lookup keys are not normalized. Inputs follow the documented row schemas; invalid options and malformed dates are not specially validated.
