# Sales service dispatcher

A small native-Python adapter over the verified `published.a01_r01` service implementations. It exposes six full-output adapters and a selective dispatcher.

```python
from candidate import run, revenue_adapter
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2, 'price_cents': 125}]
assert revenue_adapter(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
views = run(rows, [], {'fill': 'zero', 'agg': 'sum', 'window': 2}, ['clean', 'revenue'])
```

`run(rows, lookup_rows, request, families=None)` returns a dict keyed by family; omitted families computes all six. `families` may contain any of `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`; unknown names raise `ValueError`, and an empty iterable returns `{}`. Each root adapter (`clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, `window_adapter`) takes `(rows, lookup, request)` and returns that service's complete output. Input rows, lookup rows, and request are not mutated. Fill modes are zero/mean/median; aggregations sum/mean/count; window widths 2/3/4. Semantics follow the named service contract. Requires the declared `a01_r01` package; no external dependencies. Inputs are expected as lists of dictionaries in the service schema.
