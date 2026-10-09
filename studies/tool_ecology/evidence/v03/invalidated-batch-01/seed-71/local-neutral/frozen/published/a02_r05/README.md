# Tabular services

This package exposes six adapters. Each takes `(rows, lookup, request)` and returns a newly constructed result without mutating inputs:

* `clean(rows, lookup, request)`: normalized regions and filled units.
* `revenue(...)`: clean transformations plus `revenue_cents`.
* `group(...)`: region-level aggregation.
* `monthly(...)`: month/region aggregation.
* `lookup_service(...)`: revenue per exact region target.
* `window(...)`: trailing row-window revenue mean.

`request` requires `fill` (`zero`, `mean`, or `median`); aggregation services also require `agg` (`sum`, `mean`, or `count`), and window requires integer `window` size. Example:

```python
from candidate import revenue
out = revenue([{'region': ' West ', 'units': None, 'price_cents': 250}], [], {'fill': 'zero'})
assert out[0]['region'] == 'west' and out[0]['revenue_cents'] == 0
```

Lookup records must provide exact normalized `region` keys and `target`. Inputs follow the documented service schema; malformed values are not normalized beyond the specified region strip/lower operation. Implementations reuse the verified `published.a07_r04` services (and its declared dependencies).
