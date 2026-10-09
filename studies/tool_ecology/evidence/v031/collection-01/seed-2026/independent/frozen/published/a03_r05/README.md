# Tabular service toolkit

The package exports six callables, each with signature `(rows, lookup, request)`.
They return new results and do not mutate the provided row dictionaries, lookup
records, or request. The implementation is the verified dependency
`published.a03_r02` (pure Python; no third-party dependencies).

* `clean`: normalize string `region` using strip/lower and fill missing `units`.
* `revenue`: fill missing `units` and append `revenue_cents`; does not normalize
  region. Revenue is `None` if units or price is missing.
* `group`: normalize region, derive revenue, drop missing region keys and return
  per-region `<agg>_revenue_cents`.
* `monthly`: as group, additionally groups by `date[:7]`, dropping missing month
  or region and returning `month`, `region`, and aggregate.
* `lookup`: normalize region and derive revenue, then append
  `revenue_cents_per_target`. Unknown keys, missing/zero targets, and missing
  revenue yield `None`; lookup fields are not copied to output.
* `window`: derive revenue without region normalization and append the mean of
  nonmissing revenues in each trailing ROWS window including the current row.

`request['fill']` must be `zero`, `mean`, or `median`; an all-missing units
column fills with zero, and even medians average the two central values.
`request['agg']` for group/monthly must be `sum`, `mean`, or `count`; null
revenues are excluded, count counts nonnull revenues, empty sum/count are zero,
and empty mean is `None`. `request['window']` for window must be 2, 3, or 4.
Invalid parameters raise `ValueError`. All input columns are retained in
row-oriented services; existing derived-name keys are overwritten.

Example:

```python
from candidate import revenue, group
rows = [{'region': 'West', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 0}
]
```
