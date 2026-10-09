# Target lookup adapter

`lookup(rows, lookup, request)` returns fresh row dictionaries in input order,
normalizing string regions with strip/lower, filling missing units according to
`request['fill']` (`zero`, `mean`, or `median`), adding `revenue_cents`, and
adding `revenue_cents_per_target`. A missing/zero target, missing revenue, or
unknown region yields a `None` ratio. Original fields are preserved and no
lookup fields are added. Neither input is mutated.

This package reuses the tested implementation `published.a03_r01.lookup_rate`.

```python
from candidate import lookup
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
print(lookup(rows, [{'region': 'west', 'target': 10, 'manager': 'A'}],
             {'fill': 'zero'}))
# [{'region': 'west', 'units': 2, 'price_cents': 25,
#   'revenue_cents': 50, 'revenue_cents_per_target': 5.0}]
```
