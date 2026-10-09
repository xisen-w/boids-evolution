# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`.
All accept a list of row dictionaries, lookup dictionaries, and a request
mapping; return a new list of dictionaries and do not mutate inputs. The
`lookup` parameter is unused except by the lookup service. These root
adapters reuse `published.a04_r01` (declared dependency).

- `clean`: strip/lower non-null regions; fill missing units.
- `revenue`: fill units and append `revenue_cents` (null if units or price
  are missing).
- `group`: aggregate revenue per normalized region; omit null regions.
- `monthly`: aggregate per month (`date[:7]`) and normalized region; omit
  null keys.
- `lookup`: append `revenue_cents_per_target`; exact normalized region-key
  matching; null for missing revenue/target or zero target.
- `window`: append trailing `roll_revenue_cents`, a mean of non-null revenue
  values in the last `request.window` rows including current.

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`); all
missing units fill with zero. `request.agg` accepts `sum`, `mean`, or `count`
(default `sum`); count counts non-null revenues. `request.window` is 2, 3,
or 4. Empty sums/counts are zero; empty means are null. Aggregates sort by
stringified keys. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Inputs are expected to conform to the service schema (mapping rows and valid
options); date prefixes are sliced, not calendar-validated. Invalid fill,
aggregate, or window options raise `ValueError`.
