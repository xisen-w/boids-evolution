# Sales table service adapters

Imports the verified native implementations in `published.a01_r01`; no local reimplementation is required. Public functions `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` accept row dictionaries, lookup dictionaries and a request dictionary, and return the corresponding service output. Inputs are not mutated.

`request.fill` supports `zero`, `mean`, `median`; `request.agg` supports `sum`, `mean`, `count`; `request.window` supports 2, 3, or 4. Grouped outputs omit missing keys. `analyze(rows, lookup_rows, request)` returns a dictionary mapping all six family names to their outputs (so request must provide parameters valid for each service).

```python
from candidate import revenue, analyze
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2, 'price_cents': 125}]
req = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert revenue(rows, [], req)[0]['revenue_cents'] == 250
assert set(analyze(rows, [], req)) == {'clean', 'revenue', 'group', 'monthly', 'lookup', 'window'}
```
