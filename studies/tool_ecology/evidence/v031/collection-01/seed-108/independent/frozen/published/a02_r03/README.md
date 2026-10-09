# Row-table services

Import the package from its publication namespace (or import its functions):

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125, 'date': '2025-01-03'}]
cleaned = clean(rows, [], {'fill': 'zero'})
assert cleaned[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Every function has the API `service(rows, lookup, request)` and returns a new list without mutating inputs. `clean` normalizes region and fills missing units; `revenue` fills units and adds revenue; `group` and `monthly` aggregate by normalized region, optionally month; `lookup` adds revenue per region target; `window` adds trailing row-window mean revenue. Request options are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4). Missing revenue is excluded from aggregation and rolling means. Group outputs omit missing keys. Lookup does not add target or manager columns.

The package depends on the published `a02_r02` implementation; it intentionally provides the same semantics and limitations as that dependency. Inputs are expected to be row dictionaries and request/lookup values described by the service contract.
