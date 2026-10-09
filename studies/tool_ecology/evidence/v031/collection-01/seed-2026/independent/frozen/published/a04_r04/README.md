# Tabular service adapters

Public root API: `clean(rows, lookup, request)`, `revenue(rows, lookup,
request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes
row and lookup lists of dictionaries plus a request dictionary, returns a new
list, and does not mutate its inputs. Implementations are re-exported from the
verified `published.a04_r01` dependency.

- `clean`: normalize non-null regions with strip/lower; fill missing units.
- `revenue`: fill units and derive `revenue_cents` (null if an operand is null).
- `group`: normalize/derive revenue, omit null regions, aggregate by region.
- `monthly`: aggregate by month and region, omitting either null key.
- `lookup`: append `revenue_cents_per_target` using normalized exact region keys.
- `window`: append trailing-row mean `roll_revenue_cents`.

`request.fill` supports zero/mean/median (default zero); all-missing fills zero.
`request.agg` supports sum/mean/count (default sum), where count excludes null
revenue. `request.window` must be 2, 3, or 4. Empty sum/count are zero and empty
mean is null. Aggregates sort lexicographically by stringified keys. Lookup
unknown/null/zero targets yield null. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Rows are expected to follow the stated service schema and options; invalid fill,
aggregate, or window values raise `ValueError`.
