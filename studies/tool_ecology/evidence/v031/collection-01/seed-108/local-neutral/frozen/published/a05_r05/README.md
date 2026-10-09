# Table services

Native Python adapters, backed by the received and service-verified `a05_r03`.
All public functions take `(rows, lookup, request)` and return a new list of
row dictionaries (or grouped dictionaries); input data is not mutated.

* `clean`: normalize non-null region strings with strip/lower and fill missing
  units by `request['fill']` (`zero`, `mean`, or `median`; default `zero`).
* `revenue`: fill units and append `revenue_cents`, null when units or price
  are null.
* `group`: normalize/derive revenue and group non-null regions, using
  `request['agg']` (`sum`, `mean`, `count`; default `sum`).
* `monthly`: group by non-null `date[:7]` and normalized region with the same
  aggregation policies.
* `lookup_service`: append `revenue_cents_per_target` using exact normalized
  region matching; missing/zero target or missing revenue produces null.
* `window`: append trailing-row (including current) mean of non-null revenue;
  `request['window']` must be 2, 3, or 4.

Grouped outputs are sorted by stringified keys. Mean of an empty aggregate is
null; sum/count are zero. Example:

```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 8}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 8, 'revenue_cents': 0}]
```
