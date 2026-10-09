# Row transform facade

This small native-Python package exposes the six verified row-oriented table services from the received `a00_r02` implementation. It intentionally delegates rather than reimplementing the transformation semantics.

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a fresh list of dictionaries and does not mutate its inputs. Details of fill (`zero`/`mean`/`median`), aggregation (`sum`/`mean`/`count`), normalized-region boundaries, and trailing ROWS windows follow the received implementation. Window width must be 2, 3, or 4.

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Limitations: this is a compatibility facade and requires `published.a00_r02` on the import path; no extra semantics are introduced.
