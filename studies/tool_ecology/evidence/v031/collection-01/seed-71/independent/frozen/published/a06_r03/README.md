# Tabular transformations

This package exposes six native Python functions, each with the signature
`(rows, lookup, request)`. They delegate to the verified `published.a06_r02`
implementation (declared dependency). Inputs are lists of mapping-like row
records; calls return fresh dictionaries without mutating rows, lookup, or
request. The `lookup` argument is relevant only to the lookup service.

* `clean`: strip/lower region and fill missing units; preserve all row columns/order.
* `revenue`: fill units and append `revenue_cents`; region is unchanged.
* `group`: normalize region, derive revenue, and aggregate by region, excluding missing regions.
* `monthly`: normalize region and group derived revenue by `date[:7]` and region; missing keys are excluded.
* `lookup`: normalize region and append `revenue_cents_per_target` from normalized exact region matches.
* `window`: derive revenue and append `roll_revenue_cents`, a mean over trailing rows including current; region is unchanged.

`request.fill` is `zero`, `mean`, or `median` (default `zero`; all missing fills
with zero; even median averages the central pair). `request.agg` is `sum`,
`mean`, or `count` (default `sum`); count includes only nonmissing revenue.
`request.window` is a positive integer (default 2). Empty sum/count groups produce
zero and empty means produce `None`. Lookup returns `None` for unknown/missing
or zero targets and missing revenue. Grouped outputs sort keys lexically by
string representation. Inputs are expected to follow the service schema; malformed
records and unsupported parameter values are outside the API contract.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': None, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 50, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 0}]
```
