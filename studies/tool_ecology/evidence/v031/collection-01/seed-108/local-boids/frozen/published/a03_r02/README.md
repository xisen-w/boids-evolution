# Native row services

The package exports `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`. Each returns a new list of dictionaries and does not modify input values. Service adapters with `_service` suffix are aliases.

Rows are dict records. `clean` normalizes string regions with strip/lower and fills null units; `revenue` fills units and appends `revenue_cents`; `group` and `monthly` normalize region, derive revenue and aggregate (request `agg` = `sum`, `mean`, or `count`; defaults to sum). `lookup` normalizes region and adds `revenue_cents_per_target` based on the supplied region-to-target records. `window` adds a trailing-row mean with request `window` (default 2). Fill policy request `fill` accepts `zero`, `mean`, or `median` and defaults to zero. All-missing units become zero. Missing revenue is ignored in aggregates; empty mean is null.

Example:
```python
from candidate import revenue
rows = [{'region':'West','units':2,'price_cents':125}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 250
```
Missing fields are treated as null where relevant. Region values that are not strings are retained. Inputs are expected to follow the specified service schema; invalid fill/aggregation values raise ValueError.
