# Candidate row services

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)` are
available from the package root. They return fresh dictionaries and do not
mutate arguments. These are re-exports of `published.a04_r02`.

`request['fill']` supports `zero`, `mean`, and `median` (default `zero`); all
missing units fill with zero. `request['agg']` supports `sum`, `mean`, and
`count` (default `sum`). `request['window']` sets trailing ROWS width (default
2). Clean/group/monthly/lookup normalize string regions using strip/lower;
revenue and window retain region spelling. Row outputs retain original keys and
append derived keys. Revenue is null if units or price is null. Groups omit null
keys and ignore null revenues; empty sum/count are zero and empty mean is null.
Lookup adds only `revenue_cents_per_target` (null on unknown/null/zero target or
null revenue); it does not add target or manager. Monthly groups on YYYY-MM and
normalized region. Window means use nonmissing revenues within the trailing
row window and return null when that window has no values. Invalid modes raise
ValueError. Inputs are lists of dicts with the service fields documented by the
host; malformed dates/types are outside the intended interface.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' N ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'n', 'sum_revenue_cents': 100}]
```
