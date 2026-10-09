# Table service adapters

This package provides the six recurring pure-Python table operations and a named dispatcher. It delegates the service semantics to the verified `published.a01_r02` implementation.

Each adapter has signature `(rows, lookup, request)` and returns the complete service result:

* `clean(rows, lookup, request)` normalizes regions and fills missing units.
* `revenue(rows, lookup, request)` fills units and adds revenue cents.
* `group(rows, lookup, request)` aggregates revenue by region.
* `monthly(rows, lookup, request)` aggregates by month and region.
* `lookup_service(rows, lookup, request)` adds revenue per region target (named `lookup_service` in Python to avoid shadowing the lookup argument).
* `window(rows, lookup, request)` adds trailing-row rolling revenue means.

`run(family, rows, lookup, request)` dispatches using one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`; unsupported names raise `ValueError`.

Example:
```python
from candidate import run
rows = [{'id': 1, 'region': ' North ', 'product': 'x', 'date': '2025-01-02', 'units': 2, 'price_cents': 50, 'cost_cents': 20}]
result = run('revenue', rows, [], {'fill': 'zero'})
```
The imported adapters implement the family rules including missing-value behavior, ordering, and nonmutation. Requests must provide the parameters required by their family (`fill`, `agg`, or `window`).
