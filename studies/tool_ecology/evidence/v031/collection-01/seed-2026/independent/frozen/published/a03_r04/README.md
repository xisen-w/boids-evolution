# Tabular transformations

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Each callable accepts `(rows, lookup, request)` and returns fresh dictionaries/lists without mutating inputs. The implementation is provided by the declared `a03_r02` dependency.

- `clean`: strip/lower region and fill missing units.
- `revenue`: fill units and append `revenue_cents` (region is not normalized).
- `group`: normalize region, derive revenue, aggregate by region.
- `monthly`: as above, grouped on month (`date[:7]`) and region.
- `lookup`: normalize region, derive revenue, append per-target revenue; does not append lookup fields.
- `window`: derive revenue and add a trailing ROWS mean including current row.

`request['fill']` is `zero`, `mean`, or `median`; all-missing units fill with zero. `request['agg']` is `sum`, `mean`, or `count`. Aggregations exclude missing revenue; grouping drops missing keys, with empty mean `None` (sum/count are zero). `request['window']` is 2, 3, or 4. Revenue is `None` if units or price is missing. Unknown regions and missing/zero targets produce `None`. Invalid parameter values raise `ValueError`.

Example:

```python
from candidate import revenue
assert revenue([{'units': None, 'price_cents': 25}], [], {'fill': 'zero'}) == [
    {'units': 0, 'price_cents': 25, 'revenue_cents': 0}
]
```
