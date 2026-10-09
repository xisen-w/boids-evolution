# Native tabular service helpers

Pure-Python functions accept `(rows, lookup, request)` and return fresh dictionaries without mutating inputs. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

- `clean`: strip/lower region and fill missing units.
- `revenue`: fill missing units and append `revenue_cents` (does not normalize region).
- `group` / `monthly`: normalize region, derive revenue, aggregate nonmissing revenue by region or month+region.
- `lookup`: normalize region, derive revenue and append `revenue_cents_per_target` using exact region lookup.
- `window`: derive revenue and append trailing row-window mean, including current row (does not normalize region).

Fill choices are `zero`, `mean`, and `median` (default zero); all-missing units fill with zero. Aggregations are `sum`, `mean`, and `count` (default sum). Window sizes are 2, 3, or 4. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Input schema follows the service contract: rows are mappings with region/units/price_cents and monthly additionally uses date; lookup entries have region/target. Missing revenue operands produce `None`. Invalid fill/aggregation/window values raise `ValueError`.
