# Sales table service adapters

This package exposes six row-table service adapters, delegating to the verified
`published.a01_r01` implementation, and a convenience `analyze` bundle.

Each adapter accepts `(rows, lookup_rows, request)` and returns that service's
specified output: `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`.
Rows/lookup are lists of dictionaries. `request.fill` is `zero`, `mean`, or
`median`; grouped services use `request.agg` (`sum`, `mean`, `count`); window
uses `request.window` (2, 3, or 4). Inputs are not mutated.

```python
from candidate import revenue, analyze
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2,
         'price_cents': 125}]
req = {'fill': 'zero', 'agg': 'sum', 'window': 2}
assert revenue(rows, [], req)[0]['revenue_cents'] == 250
views = analyze(rows, [], req)
assert set(views) == {'clean', 'revenue', 'group', 'monthly', 'lookup', 'window'}
```

`analyze` evaluates every adapter and therefore requires the union of their
request parameters. It returns a dict keyed by family name; each value has the
same schema as calling that adapter directly. Invalid parameter handling and
all service semantics follow the upstream implementation.
