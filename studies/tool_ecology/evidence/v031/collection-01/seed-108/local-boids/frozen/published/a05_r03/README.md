# Row-table service facade

This package provides six pure service functions through a verified implementation (`published.a05_r02`). Each function accepts `(rows, lookup, request)` and returns the family result without modifying caller inputs.

* `clean(rows, lookup, request)`: normalized region and filled units, preserving columns and row order.
* `revenue(...)`: filled units and derived revenue.
* `group(...)`: region aggregate.
* `monthly(...)`: month/region aggregate.
* `lookup(...)`: lookup-based revenue per target.
* `window(...)`: trailing row-window revenue mean.

Request fields are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`) and `window` (2/3/4), as applicable. Example:

```python
from candidate import clean
result = clean([{'region': ' West ', 'units': None, 'price_cents': 100}], [], {'fill': 'zero'})
```

The facade intentionally delegates semantics to its declared dependency rather than implementing a second copy. It requires `published.a05_r02` to be available.
