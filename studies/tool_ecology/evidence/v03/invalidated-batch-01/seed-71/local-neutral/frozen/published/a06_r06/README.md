# Row-table services

This package exposes six native Python functions, each with signature
`service(rows, lookup, request)`. Functions return fresh results and do not
mutate any input.

* `clean`: strip and lowercase each region; fill missing units using
  `request['fill']` (`zero`, `mean`, or `median`; all-missing fills with 0).
* `revenue`: the clean unit-fill behavior plus `revenue_cents`, the product of
  units and price, or `None` if either is missing.
* `group`: normalize regions and compute revenue; discard missing regions,
  aggregate nonmissing revenue according to `request['agg']` (`sum`, `mean`,
  `count`) into `region` and `<agg>_revenue_cents`, sorted by stringified region.
* `monthly`: as above, grouping by `date[:7]` and region; missing month or
  region is excluded. Results are sorted by stringified month then region.
* `lookup`: normalize regions and compute revenue, then append
  `revenue_cents_per_target` using an exact region key in lookup rows. Unknown
  keys, absent/zero targets, and missing revenue yield `None`. Does not append
  target or manager.
* `window`: compute revenue and append `roll_revenue_cents`, the mean of
  nonmissing revenues in the trailing `request['window']` rows (including the
  current row); no values yields `None`.

Row-level services preserve input columns and row order. Group services return
only their documented output columns. Input rows are dictionaries; lookup is a
list of dictionaries. Requests must supply the relevant `fill`, `agg`, or
`window` value. Example:

```python
from candidate import revenue
rows = [{'units': None, 'price_cents': 50}, {'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'mean'})
# [{'units': 2.0, 'price_cents': 50, 'revenue_cents': 100.0},
#  {'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

These functions are re-exported from the verified `published.a06_r05`
implementation; invalid modes or malformed inputs are outside the supported
contract and may raise exceptions. Lookup matching is exact (only row regions
are normalized).
