# Tabular services and batch dispatch

The package reuses `published.a07_r05` for the six service families. Root
adapters `clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`,
`lookup_adapter`, and `window_adapter` each accept `(rows, lookup, request)`.

`process(family, rows, lookup, request)` dispatches a named service and raises
`ValueError` for an unknown family. `process_many(jobs)` evaluates four-item
jobs `(family, rows, lookup, request)` in order and stops on errors.
`process_iter(jobs)` lazily yields their outputs, with errors propagating when
reached. `process_results(jobs)` evaluates every job once and returns
`(success, value)` pairs; failures are `(False, exception)` and do not stop
later jobs.

```python
from candidate import process, process_results
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert process('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
jobs = [('revenue', rows, [], {'fill': 'zero'}),
        ('not-a-family', rows, [], {})]
assert process_results(jobs)[0][0] is True
assert process_results(jobs)[1][0] is False
```

Services preserve the specified table semantics: normalization, filling,
aggregation, lookup, and rolling window behavior follow the corresponding
service definitions. Inputs are expected to be lists of row mappings and
requests to provide applicable parameters. `process_results` catches ordinary
`Exception` subclasses (not process-control exceptions); it does not retry or
roll back side effects in user-supplied iterables.
