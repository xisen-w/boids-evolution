# Row service batch dispatcher

Exports `apply(family, rows, lookup, request)`, `apply_many(jobs)`, and six full-service adapters: `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_adapter`, and `window_service`. The adapters and dispatcher delegate to the independently verified `published.a00_r02` implementations and preserve their semantics (fill zero/mean/median; aggregation sum/mean/count; trailing row windows 2/3/4). Inputs are not mutated by those services.

`apply_many` accepts an iterable of mappings, each containing `family`, `rows`, `lookup`, and `request`; results are returned in job order. An invalid family or malformed job raises an exception and terminates the batch; it does not return per-job errors.

```python
from candidate import apply_many
jobs = [dict(family='revenue', rows=[{'units': 2, 'price_cents': 50}],
             lookup=[], request={'fill': 'zero'})]
assert apply_many(jobs) == [[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]]
```

Tables follow the row-service API. This package adds batching, not new transformation semantics.
