# Row-table service facade

Imports and re-exports six pure Python services from the verified `published.a04_r02` package. Public call signature for every function is `service(rows, lookup, request)`; arguments are row dictionaries, lookup dictionaries, and a request dictionary. The returned value is a new list; inputs are not modified.

* `clean`: normalize string regions with strip/lower; fill missing units.
* `revenue`: fill missing units and append `revenue_cents`.
* `group`: normalized region aggregation, dropping missing region keys.
* `monthly`: group by `date[:7]` and normalized region, dropping missing keys.
* `lookup`: adds exact normalized-region `revenue_cents_per_target`; does not add target/manager fields.
* `window`: append trailing-row mean `roll_revenue_cents`.

`request['fill']` accepts `zero`, `mean`, or `median` (default `zero`); all-missing values fill with zero, and an even median averages its central pair. Group services accept `request['agg']` of `sum`, `mean`, or `count` (default `sum`), ignoring missing revenues; empty sum/count is zero and empty mean is `None`. Window accepts `request['window']` 2, 3, or 4 (default 2). Invalid option values raise `ValueError`. Lookup returns `None` for unknown regions, absent/zero targets, or missing revenue.

Example:
```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
result = revenue(rows, [], {'fill': 'zero'})
# [{'region': 'West', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
