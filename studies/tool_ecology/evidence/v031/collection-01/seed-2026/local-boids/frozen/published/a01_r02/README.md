# Lookup adapter

`lookup(rows, lookup, request)` returns a new list of row dictionaries. It normalizes non-null regions with strip/lower, fills missing units using `request['fill']` (`zero`, `mean`, or `median`; all missing becomes zero), derives `revenue_cents`, and appends `revenue_cents_per_target`. Target regions are normalized identically. Unknown regions, missing/zero targets, or missing revenue produce `None`. Original fields are preserved; inputs are not mutated. It does not add target or manager columns.

Example:

```python
from candidate import lookup
result = lookup([{'region':' West ', 'units':2, 'price_cents':50}],
                [{'region':'west', 'target':2, 'manager':'A'}], {'fill':'zero'})
# region='west', revenue_cents=100, revenue_cents_per_target=50
```

Requires the declared `a02_r01` package. Only the lookup family is exposed.
