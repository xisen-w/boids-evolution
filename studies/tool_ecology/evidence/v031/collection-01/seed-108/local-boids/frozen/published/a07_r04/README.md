# Row-table services

Exports `clean(rows, lookup_rows, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`, with matching `_service` aliases. Each returns new dictionaries, preserving input row ordering where applicable, and does not mutate inputs. `run(family, rows, lookup_rows, request)` dispatches to any of the six services, rejecting unknown family names with `ValueError`.

Rows are dictionaries. Region strings are stripped and lowercased where that family specifies normalization. Missing units use request `fill` (`zero`, `mean`, `median`; all-missing becomes zero). Revenue is units times price, or `None` if either is missing. Group/monthly aggregate nonmissing revenue with `agg` (`sum`, `mean`, `count`); monthly keys are date prefixes. Lookup adds per-target revenue and window adds trailing-row mean. See the service contract for exact output columns and sorting.

Example:
```python
from candidate import run
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert run('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

This package delegates computation to received native implementation `published.a03_r02`; it adds a uniform dispatcher and stable adapter exports. Inputs are expected to conform to the row-table schema; invalid fill/aggregation policies raise `ValueError`.
