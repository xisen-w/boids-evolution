# Row services

This package re-exports the six tested native-Python services from `published.a07_r02`.
Functions take `(rows, lookup, request)` and return new dictionaries without mutating
inputs: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. See that
package's documentation for fill (`zero`/`mean`/`median`), aggregation
(`sum`/`mean`/`count`), normalization and rolling-window semantics. Numeric input
values are expected; invalid modes raise `ValueError`.

```python
from candidate import revenue
result = revenue([{'units': 2, 'price_cents': 150, 'region': ' West '}], [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 300
assert result[0]['region'] == ' West '  # revenue preserves original region
```
