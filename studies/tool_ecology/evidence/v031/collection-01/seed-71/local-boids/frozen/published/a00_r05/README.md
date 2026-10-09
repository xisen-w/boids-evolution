# Row-table service dispatcher

Provides `process(family, rows, lookup, request)` and six root service adapters: `clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, and `window_adapter`. Each adapter accepts `(rows, lookup, request)` and returns the complete result for its family. `process` accepts one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`, and raises `ValueError` for an unknown family.

```python
from candidate import process
rows = [{'region': 'West', 'units': 2, 'price_cents': 75}]
assert process('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 150
```

Transformation, ordering, null behavior, parameter handling, and limitations are those of the verified adapters in `published.a07_r03`; this package adds only dispatch and does not mutate input data itself.
