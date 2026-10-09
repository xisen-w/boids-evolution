# Table service dispatcher

This package supplies `run(family, rows, lookup, request)` and direct adapters
`clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`,
`lookup(...)`, and `window(...)`. It delegates the service semantics to the
verified native implementation in `published.a04_r05`.

`family` is exactly one of `clean`, `revenue`, `group`, `monthly`, `lookup`,
`window`; an unknown name raises `ValueError`. Inputs are lists of row/lookup
dictionaries and a request dictionary and are not mutated. Fill behavior,
aggregation, sorting, missing-value rules, and output schemas are documented
in the service contract (also available in `published.a04_r05`).

```python
from candidate import run
rows = [{'region': ' West ', 'units': 2, 'price_cents': 25}]
result = run('revenue', rows, [], {'fill': 'zero'})
# [{'region': ' West ', 'units': 2, 'price_cents': 25, 'revenue_cents': 50}]
```
