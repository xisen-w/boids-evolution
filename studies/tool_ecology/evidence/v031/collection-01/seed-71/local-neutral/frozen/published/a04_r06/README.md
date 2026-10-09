# Tabular services

Native Python transformations; public functions take `(rows, lookup, request)` and return new lists/dicts without modifying inputs. Missing values are represented by `None`.

- `clean`: normalized region and filled units; retains all columns.
- `revenue`: clean output plus `revenue_cents` (`None` if units or price is missing).
- `group`: rows grouped by normalized nonmissing region, with `<agg>_revenue_cents`.
- `monthly`: grouped by nonmissing month and normalized region, with `<agg>_revenue_cents`.
- `lookup_service`: revenue output plus per-target revenue; targets match normalized region keys.
- `window`: revenue output plus trailing-row `roll_revenue_cents`.

`request.fill` supports `zero`, `mean`, and `median` (even medians average central values; all missing fills to zero). `request.agg` supports `sum`, `mean`, and `count`; count excludes missing revenue. `request.window` is a trailing row count. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 10}]
assert group(rows, [], {'fill':'zero','agg':'sum'}) == [
    {'region':'west', 'sum_revenue_cents':20}]
```

Input schema follows the service contract; no validation of malformed row types or unsupported request options is promised.
