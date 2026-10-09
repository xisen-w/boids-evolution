# Row table adapters

This package exposes six pure service adapters, each with the exact call signature
`family(rows, lookup_rows, request) -> list[dict]`: `clean`, `revenue`, `group`,
`monthly`, `lookup`, and `window`. They delegate to the tested
`published.a07_r05` implementation, which is included as a declared dependency.

Rows and lookup tables are lists of dictionaries; request is a dictionary. Inputs
are not mutated. `clean` strips/lowercases regions and fills missing units using
`fill` equal to `zero`, `mean`, or `median` (all-missing gives zero; even median
averages the middle pair). `revenue` adds `revenue_cents`, null if either operand
is null. `group` groups normalized region; `monthly` groups month (date prefix
YYYY-MM) and region; both drop missing keys and aggregate nonmissing revenue by
`agg` (`sum`, `mean`, or `count`). Empty sum/count are zero and empty mean is
null. `lookup` adds `revenue_cents_per_target` based on exact normalized region
keys, null for unknown/missing/zero target or missing revenue. `window` adds the
trailing ROWS average `roll_revenue_cents` using `window` width. Row operations
preserve row order and columns and append derived values; grouped output sorts by
stringified keys. Numeric inputs are expected. Duplicate lookup keys use the
underlying dependency behavior (last entry wins).

Example:
```python
from candidate import revenue
out = revenue([{'units': 2, 'price_cents': 25}], [], {'fill': 'zero'})
assert out[0]['revenue_cents'] == 50
```
