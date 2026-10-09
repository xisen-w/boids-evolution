# Native tabular service helpers

Import `clean`, `revenue`, `group`, `monthly`, `lookup_service`, or `window` from this package. All take `(rows, lookup, request)` and return new lists/dicts without mutating arguments. Matching `serve_clean`, `serve_revenue`, `serve_group`, `serve_monthly`, `serve_lookup`, and `serve_window` adapters expose the same interface.

`clean` strip/lower normalizes string regions and fills missing `units`; `revenue` does the same and appends `revenue_cents`, null if units or price is missing. `group` aggregates revenue by nonmissing region; `monthly` aggregates by nonmissing `date[:7]` and region. Both return only keys plus the requested aggregate column, sorted by stringified keys. `lookup_service` adds `revenue_cents_per_target` from strip/lower normalized exact lookup regions (null for unknown/missing/zero target or missing revenue), without adding lookup fields. `window` adds `roll_revenue_cents`, a mean over nonmissing revenues within the trailing positional window including the current row.

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`); empty/all-null units fill with zero. `request.agg` accepts `sum`, `mean`, or `count` (default `sum`); count counts non-null revenue. `request.window` accepts 2, 3, or 4. Sum/count of an empty group are zero; mean is null. Row transformations preserve original columns and order; aggregate services intentionally output only aggregate columns. Inputs should conform to the documented service schema and valid parameters; malformed inputs are not normalized/coerced.

Example:
```python
from candidate import revenue, group
rows = [{'region':' North ', 'units':None, 'price_cents':5}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill':'zero','agg':'sum'}) == [{'region':'north','sum_revenue_cents':0}]
```
