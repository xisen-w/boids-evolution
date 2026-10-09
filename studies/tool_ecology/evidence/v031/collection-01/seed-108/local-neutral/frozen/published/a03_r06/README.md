# Row-table services

Native-Python package exporting `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`; each function has the signature `(rows, lookup, request)` and returns a new result without mutating its inputs. The corresponding `*_service` names are the publication's service-check adapters.

```python
from candidate import revenue, group
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-04', 'units': 2, 'price_cents': 125, 'cost_cents': 40}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [{'region': 'west', 'sum_revenue_cents': 250}]
```

`fill` supports `zero`, `mean`, or `median` (default `zero`); `agg` supports `sum`, `mean`, or `count` (default `sum`); `window` selects trailing row count 2, 3, or 4. Clean normalizes region and fills units. Revenue preserves original fields and adds `revenue_cents`; group/monthly return sorted aggregates; lookup adds `revenue_cents_per_target` using exact normalized region lookup; window adds trailing-row mean. Grouped services drop missing keys. Lookup does not append target or manager. The API expects the documented row/lookup dictionary schema and valid request options; it has no external dependencies beyond the explicitly declared received package.
