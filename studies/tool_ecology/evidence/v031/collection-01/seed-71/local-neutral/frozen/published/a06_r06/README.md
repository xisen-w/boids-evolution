# Table service facade

This native Python package exposes the tested six-family table transformation
API from `published.a06_r04`, without reimplementing it. All service adapters
accept `(rows, lookup, request)` and return fresh results without mutating inputs.

Public functions: `clean`, `revenue`, `group`, `monthly`, `lookup_revenue`,
`window`, and adapter names `clean_service`, `revenue_service`, `group_service`,
`monthly_service`, `lookup_service`, `window_service`. Adapters correspond to
same-named families; lookup uses `lookup_revenue` internally.

Request options: fill (`zero`, `mean`, `median`), agg (`sum`, `mean`, `count`),
and window size (2, 3, or 4). Missing units are filled (all missing -> 0); even
median averages central values. Revenue is null if an operand is null. Grouping
normalizes region and omits missing keys; count counts nonmissing revenue.
Monthly grouping uses the first seven date characters. Lookup matches normalized
region keys and returns null for unknown/zero/missing targets. Rolling means use
the trailing number of rows including current, ignoring missing revenue values.

Example:
```python
from candidate import revenue_service
rows = [{"units": 2, "price_cents": 50}]
assert revenue_service(rows, [], {"fill": "zero"})[0]["revenue_cents"] == 100
```
Limitations: dates are expected to be strings supporting `[:7]`; inputs follow
the documented row schema and valid request choices.
