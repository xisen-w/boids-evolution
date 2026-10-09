# Tabular services and pipelines

Exports six host-compatible adapters `clean_service(rows, lookup_rows, request)`,
`revenue_service(...)`, `group_service(...)`, `monthly_service(...)`,
`lookup_service(...)`, and `window_service(...)`. Each delegates to verified
`published.a02_r04` and follows its service schemas and fill/aggregation/window
semantics. The lookup-table argument is unused except by lookup enrichment.

`run_pipeline(rows, lookup_rows, requests)` applies an iterable of
`(family, request)` pairs in order, feeding each output to the next step:

```python
from candidate import run_pipeline
out = run_pipeline(rows, lookup_rows, [
    ("clean", {"fill": "median"}),
    ("window", {"fill": "zero", "window": 3}),
])
```

Supported names are `clean`, `revenue`, `group`, `monthly`, `lookup`, and
`window`; unknown names raise `ValueError`. Grouping services produce aggregate
schemas, so later row services may not be meaningful on their outputs. Requests
are supplied per step and must meet the underlying service's requirements.
