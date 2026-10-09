# Candidate row-table services

This package exposes six non-mutating service adapters, each accepting
`(rows, lookup_rows, request)` and returning fresh output dictionaries.

* `clean`: normalize region with strip/lower and fill missing units.
* `revenue`: fill missing units and add `revenue_cents`.
* `group`: normalize region, derive revenue, aggregate by region.
* `monthly`: group derived revenue by month and normalized region.
* `lookup`: append `revenue_cents_per_target`, without adding lookup metadata.
* `window`: append trailing physical-row mean `roll_revenue_cents`.

Request options: `fill` is `zero`, `mean`, or `median` (default `zero`);
`agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4.
Lookup rows use `region` and `target`. Missing group keys are omitted;
aggregates ignore missing revenue, with empty sum/count equal to zero and empty
mean equal to `None`. Unknown/zero targets and missing revenue produce a `None`
ratio. Inputs are not modified. Example:

```python
from candidate import revenue
revenue([{'units': 2, 'price_cents': 125}], [], {'fill': 'zero'})
# [{'units': 2, 'price_cents': 125, 'revenue_cents': 250}]
```

Implementations are delegated to the received, service-verified `a05_r02`
package. No additional behavior beyond these row-table APIs is promised.
