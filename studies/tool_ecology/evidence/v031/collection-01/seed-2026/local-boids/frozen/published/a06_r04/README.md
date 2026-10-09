# Table service adapters

This package re-exports the six independently verified native Python service
implementations from `published.a06_r03`. All public callables have signature
`(rows, lookup, request)` and return fresh output dictionaries; see that
package's documentation for exact transformation semantics.

```python
from candidate import revenue, monthly

rows = [{'region': ' West ', 'units': 2, 'price_cents': 50,
         'date': '2025-01-03'}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert monthly(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'month': '2025-01', 'region': 'west', 'sum_revenue_cents': 100}]
```

The APIs expect the documented table schemas and supported request values:
fill `zero`/`mean`/`median`, aggregate `sum`/`mean`/`count`, and window
width 2/3/4. ISO date strings are grouped using their `YYYY-MM` prefix.
