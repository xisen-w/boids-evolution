# Row-service dispatcher

A small native-Python named dispatcher over the verified `a00_r02` row services. This package exports `apply(family, rows, lookup, request)` and thin named adapters `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service`. Family names are `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. Arguments and service semantics are documented by the underlying package: fill is `zero`/`mean`/`median`; aggregate is `sum`/`mean`/`count`; window widths are 2/3/4. Unknown family names raise `ValueError`. Inputs are not mutated.

Example:

```python
from candidate import apply
apply('revenue', [{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

This dispatcher intentionally adds no alternate transformation semantics; it depends on `published.a00_r02` for those implementations.
