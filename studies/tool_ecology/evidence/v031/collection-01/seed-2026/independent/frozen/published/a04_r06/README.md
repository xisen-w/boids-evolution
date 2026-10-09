# Tabular service adapters

Public functions `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` each implement
the named service and return new lists of dictionaries without mutating inputs.
They are re-exported from the service-verified `published.a04_r01` implementation.

`request` supports `fill` (`zero`, `mean`, or `median`; default zero), `agg`
(`sum`, `mean`, or `count`; default sum), and `window` (2, 3, or 4 for the
window service). Missing units are filled; all-missing uses zero, and even
medians average their two central values. Revenue is null if either operand is
missing. Aggregations ignore null revenues, omit missing group keys, and sort
output keys lexically by their string representations. Empty sum/count values
are zero; empty means are null. Lookup matches normalized (strip/lower) regions;
missing/zero targets, unknown regions, and missing revenue yield null ratios.
The lookup argument is the lookup table (not a second option dictionary).
Invalid option values raise `ValueError`; inputs are expected to use the service
row schema.

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```
