# Row-table analytics

Dependency-free Python adapters: `clean(rows, lookup, request)`, `revenue(...)`,
`group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`, exported from
package root. Each returns new dictionaries/lists and does not mutate inputs.

`clean` normalizes string regions with strip/lower and fills missing units,
preserving columns and row order. Revenue-family functions fill units then
append/update `revenue_cents` (`None` if units or price is missing). Group and
monthly aggregate nonmissing revenues, dropping missing grouping keys, with
output named `<agg>_revenue_cents`; sorting is by stringified grouping keys.
Lookup uses exact normalized region keys and adds only
`revenue_cents_per_target`. Window adds trailing physical-row
`roll_revenue_cents`, including current row.

Request `fill` accepts `zero` (default), `mean`, or `median`; an all-missing
column fills with zero and even medians average the middle values. `agg` accepts
`sum` (default), `mean`, or `count` (counts nonmissing revenue); empty mean is
None and empty sum/count are zero. `window` defaults to 2 and must be a positive
integer. Unknown lookup keys, missing/zero targets, and missing revenue yield
None per target. Empty input yields empty output. Data is expected to contain
numeric units/prices, string-or-None regions, and ISO-like dates.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'north', 'sum_revenue_cents': 100}]
```
