# tabular_services

Pure-Python implementations of all six row-table service families. Public functions have the common signature `function(rows, lookup, request)`; inputs are not mutated and outputs are newly allocated dictionaries. Input dictionary keys/columns are retained, with derived keys appended. Units filling is computed from all nonmissing units in the input; all-missing units fill with zero. Regions are normalized with `strip().lower()`.

- `clean(rows, lookup, request)`: normalized rows and filled `units`.
- `revenue(rows, lookup, request)`: clean transformations plus `revenue_cents`.
- `group(rows, lookup, request)`: grouped records with normalized `region` and `<agg>_revenue_cents`.
- `monthly(rows, lookup, request)`: grouped records with `month`, `region`, and aggregate revenue.
- `lookup(rows, lookup, request)`: revenue rows plus `revenue_cents_per_target`; targets are keyed by normalized exact region.
- `window(rows, lookup, request)`: revenue rows plus `roll_revenue_cents`, a trailing physical-rows mean including current row.

`request` uses `fill` equal to `zero`, `mean`, or `median` (default `zero`), `agg` equal to `sum`, `mean`, or `count` (default `sum`), and positive integer `window` (default 2). Grouping excludes missing keys; aggregate count excludes missing revenue. Lookup outputs null for missing revenue/target, zero targets, and unknown regions. Lookup entries with duplicate normalized regions use the last entry. Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 100
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Limitations: values are expected to be numeric where arithmetic is required, dates (when present) are ISO-like strings, and invalid fill/aggregation names raise `ValueError`.
