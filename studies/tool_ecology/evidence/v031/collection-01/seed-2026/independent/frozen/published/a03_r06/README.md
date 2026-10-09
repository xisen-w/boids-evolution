# Tabular service facade

This native Python package re-exports six pure-Python service adapters from the
explicit dependency `published.a03_r05`. Each callable has signature
`(rows, lookup, request)` and returns a new result without mutating inputs:

* `clean`: strip/lower region and fill missing units, preserving row/column order.
* `revenue`: fill missing units and append `revenue_cents` (None if units or
  price is None), without region normalization.
* `group`: normalize region, derive revenue, drop missing region keys, and
  aggregate nonmissing revenues as requested.
* `monthly`: as group, additionally group by `date[:7]` and drop missing keys.
* `lookup`: normalize region, derive revenue, and append revenue per exact
  region target; unknown/missing/zero targets produce None.
* `window`: derive revenue and append the mean of nonmissing revenue values in
  the trailing `request['window']` ROWS, including current row.

`request['fill']` accepts `zero`, `mean`, or `median` (all-missing fills zero;
even median averages central values). Grouping accepts `request['agg']` of
`sum`, `mean`, or `count`; count excludes missing revenues, empty sum/count are
zero, and empty mean is None. Window sizes are 2, 3, or 4. Invalid parameters
raise ValueError. Existing derived keys are overwritten. Lookup/manager and
target columns are not copied into results.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 0}
]
```
