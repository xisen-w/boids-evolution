# Row service facade

This package re-exports six tested pure-Python services from `published.a00_r02`;
it adds no alternate implementation. Each function accepts `(rows, lookup,
request)` and returns the corresponding transformed list without mutating inputs.

* `clean`: normalize region strings and fill missing units.
* `revenue`: fill units and derive `revenue_cents`.
* `group`: aggregate revenue by normalized region.
* `monthly`: aggregate by month and normalized region.
* `lookup`: add revenue per exact region-key target.
* `window`: add trailing-row mean revenue.

Example: `candidate.revenue(rows, [], {"fill": "median"})`.

Fill modes are `zero`, `mean`, and `median` (all-missing fills with zero);
aggregations are `sum`, `mean`, and `count`; window widths are 2, 3, or 4.
The underlying API's input and missing-value semantics apply. This facade
requires the declared `a00_r02` package and intentionally contains no fork.
