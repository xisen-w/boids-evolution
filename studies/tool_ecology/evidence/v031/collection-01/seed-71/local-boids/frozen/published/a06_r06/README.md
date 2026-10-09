# Row transformation services

Pure-Python adapters for six row-table services. Each adapter has signature
`(rows, lookup, request)`, returns new data, and does not mutate arguments:
`clean` normalizes/fills; `revenue` derives revenue; `group` aggregates by
region; `monthly` groups by month and region; `lookup` adds revenue per target;
`window` adds a trailing ROWS mean. They honor fill (`zero`, `mean`, `median`),
aggregation (`sum`, `mean`, `count`), and window (2, 3, 4) parameters as
applicable, including the specified missing/empty behavior.

```python
from candidate import clean, group, run_services
request = {"fill": "median", "agg": "sum", "window": 2}
cleaned = clean(rows, [], request)
totals = group(rows, [], request)
results = run_services(["clean", "window"], rows, [], request)
```

Also exports `run_service(family, rows, lookup_rows, request)` and
`run_services(families, rows, lookup_rows, request)`. The latter returns a dict
keyed by family; repeated names overwrite earlier results. Unknown service
names raise `KeyError`. Services are delegated to verified `published.a06_r05`.
