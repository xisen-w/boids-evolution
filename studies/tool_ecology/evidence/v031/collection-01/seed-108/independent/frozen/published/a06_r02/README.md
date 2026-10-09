# Table transforms

Native Python, no dependencies. Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Each has signature `(rows, lookup, request)` and returns fresh row dictionaries without mutating arguments.

`clean` normalizes non-null regions with `strip().lower()` and fills null units according to `request['fill']` (`zero`, `mean`, or `median`; all-missing uses zero), preserving row and column order. `revenue` performs that fill and appends `revenue_cents`, null if either operand is null. `group` aggregates revenue by non-null normalized region; `monthly` aggregates by non-null month (`date[:7]`) and region. Both honor `request['agg']` (`sum`, `mean`, `count`), exclude null revenues, and sort keys; empty means are null. `lookup` appends `revenue_cents_per_target` using normalized region keys from lookup rows, null for unknown/zero/null targets or null revenue. `window` appends `roll_revenue_cents`, mean of non-null revenues in the trailing `request['window']` rows (2, 3, or 4), or null if none.

Example:

```python
from candidate import revenue
assert revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})[0]['revenue_cents'] == 100
```

Inputs are lists of mappings with service fields; aggregation and fill modes should be as listed. No external dependencies.
