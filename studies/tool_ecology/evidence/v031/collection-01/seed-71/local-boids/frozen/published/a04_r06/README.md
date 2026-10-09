# Dispatchable row-table services

Import `run` or any of the six service callables from `candidate`. Each service has the API `service(rows, lookup, request)` and returns the corresponding transformed list. `run(family, rows, lookup, request)` dispatches by one of `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`; unknown names raise `ValueError`.

```python
from candidate import run
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert run('group', rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Inputs are lists of dictionaries and are not mutated. Fill modes are `zero`, `mean`, `median` (even median averages central values; all missing fills with zero). Aggregations are `sum`, `mean`, `count` (nonmissing revenues only); incomplete grouping keys are dropped. Lookup uses normalized exact region keys and returns `None` for unavailable/zero targets or unavailable revenue. Window means use trailing rows including current, ignoring missing revenues. The six underlying functions and their validation/edge behavior are supplied by the declared `a04_r02` dependency. This package adds dispatch, not a separate computation engine.
