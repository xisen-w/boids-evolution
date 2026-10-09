# Table service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each function implements the corresponding service contract: fill modes `zero`, `mean`, `median`; aggregate modes `sum`, `mean`, `count`; window sizes 2, 3, or 4. Inputs are lists of dictionaries and are not mutated. Example:

```python
from candidate import revenue
result = revenue([{'region':' North ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})
# region remains as supplied for revenue; revenue_cents is 100
```

`clean`, grouping, monthly and lookup normalize region strings. Revenue and window preserve source columns and order while appending calculated fields; group/monthly return aggregate records. Unknown/missing lookup targets and zero targets produce `None` per contract. Values are expected to be ordinary numeric values or `None`; malformed records and unsupported request modes raise errors. This package delegates to immutable received packages `a04_r01` (five services) and `a01_r01` (lookup), which must be available on the Python import path.
