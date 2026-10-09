# table_services

Native Python implementations of six table services. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each accepts the specified list-of-dictionaries inputs and returns a new list without mutating inputs. The second argument is ignored except by the lookup service. `request.fill` is `zero`, `mean`, or `median`; aggregate APIs use `request.agg` (`sum`, `mean`, `count`), and window uses `request.window` (2, 3, or 4).

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
Missing regions remain missing; month uses the first seven characters of date. Lookup matches normalized exact region names. Invalid request options raise `ValueError`. Inputs are expected to be the documented rows with numeric units/prices/targets.
