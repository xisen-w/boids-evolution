# Sales table adapters

All public functions accept `(rows, lookup, request)` and return new data without mutating inputs. Rows are dictionaries; missing numeric values use `None`.

- `clean(rows, lookup, request)`: strip/lower non-null regions and fill missing units. Preserves row and key order.
- `revenue(...)`: fills units and adds `revenue_cents` (`None` if units or price is missing).
- `group(...)`: normalized-region aggregate output with `region` and `<agg>_revenue_cents`; missing region keys are omitted.
- `monthly(...)`: aggregates by normalized region and `date[:7]`; missing keys omitted.
- `lookup(...)`: row-preserving output with `revenue_cents_per_target`; unknown/missing/zero target or missing revenue yields `None`.
- `window(...)`: row-preserving output with trailing-ROWS `roll_revenue_cents` including current row.

Options: `request.fill` is `zero`, `mean`, or `median` (even median averages the middle pair; all missing fills with zero). `request.agg` is `sum`, `mean`, or `count` (counts nonmissing revenues). Empty aggregate values yield 0 for sum/count and `None` for mean. `request.window` is 2, 3, or 4. Groups sort lexicographically by stringified keys. Null region/date keys are excluded from aggregation.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 0}]
```

Expected input fields follow the service contract; region and date should be strings or `None`. Only standard Python and the declared `published.a05_r01` dependency are used.
