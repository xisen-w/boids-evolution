# Row services

Native Python package; no third-party dependencies. Public service functions all accept `(rows, lookup, request)` and return fresh lists and row dictionaries without mutating inputs. `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window` implement the corresponding service families; root adapters are named by `publish.json`. `lookup` is also an alias for `lookup_service`.

Rows are dictionaries. `request.fill` supports `zero`, `mean`, and `median` (default zero; all-missing becomes zero); `request.agg` supports `sum`, `mean`, and `count` (default sum); `request.window` must be 2, 3, or 4. Revenue is units times price, or `None` if price is absent. Group services drop missing keys and ignore missing revenue. Lookup normalizes both sets of region strings and adds only the per-target metric. Window averages available revenue values in the trailing N physical rows.

Example:

```python
from candidate import revenue_service, window_service
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
assert revenue_service(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 100
assert window_service(rows, [], {'fill':'zero','window':2})[0]['roll_revenue_cents'] == 100
```

Non-string regions are preserved; input schemas and numeric types are otherwise expected to follow the service contract. Invalid fill, aggregation, or window values raise `ValueError`.
