# Row table service adapters

This package provides six functions accepting `(rows, lookup, request)`, with the service semantics documented for the publication families. Each is re-exported from the tested `published.a01_r04` implementation; inputs are expected to be list-of-dict rows, lookup records, and a request mapping. Functions return fresh result rows, and leave inputs unchanged.

* `clean_service(rows, lookup, request)`: normalize region and fill missing units.
* `revenue_service(rows, lookup, request)`: fill units and derive `revenue_cents`.
* `group_service(rows, lookup, request)`: normalize/derive revenue and aggregate by region.
* `monthly_service(rows, lookup, request)`: aggregate by month and region.
* `lookup_service(rows, lookup, request)`: derive revenue per region target.
* `window_service(rows, lookup, request)`: add trailing-row revenue mean.

Example:
```python
from candidate import revenue_service
result = revenue_service([{"region": "N", "units": 2, "price_cents": 50}], [], {"fill": "mean"})
assert result[0]["revenue_cents"] == 100
```

Fill modes are zero/mean/median; aggregate modes are sum/mean/count; rolling window sizes are 2/3/4. This package does not add validation beyond its implementation or provide dataframe inputs; required row fields follow the service schema. `lookup` is unused except by the lookup service.
