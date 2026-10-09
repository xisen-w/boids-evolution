# Row-table adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each returns a fresh list of dictionaries and does not modify inputs. The `lookup` parameter is a region/target/manager list for the lookup service and can be empty otherwise.

Requests use `fill` = `zero`, `mean`, or `median`; aggregation uses `agg` = `sum`, `mean`, or `count`; window uses a trailing row width in `window`. For example:

```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 10}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 10, 'revenue_cents': 0}]
```

Clean normalizes region and fills units. Revenue derives revenue while retaining region. Group/monthly normalize region and aggregate, omitting missing grouping keys. Lookup adds revenue per matching nonzero target. Window computes trailing-row mean revenue. Inputs and request choices are expected to follow the service schemas.
