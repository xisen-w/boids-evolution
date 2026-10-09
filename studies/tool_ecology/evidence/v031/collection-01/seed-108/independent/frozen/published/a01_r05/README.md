# Table service adapters

Exports six callables at package root, each with signature `(rows, lookup, request)`. They return fresh results and do not mutate inputs. Rows and lookup entries are dictionaries following the service schema.

- `clean(rows, lookup, request)`: trim/lower region and fill missing units; preserve columns and row order.
- `revenue(...)`: fill units, add `revenue_cents` (`None` if units or price is missing).
- `group(...)`: normalize regions, derive revenue and aggregate by region, dropping missing keys.
- `monthly(...)`: group by month and normalized region, dropping missing group keys.
- `lookup(...)`: normalize region, derive revenue and append `revenue_cents_per_target` using exact region lookup.
- `window(...)`: derive revenue and append the trailing-ROWS `roll_revenue_cents` mean.

`request.fill` accepts `zero`, `mean`, or `median`; even medians average the central pair and all-missing units fill with zero. `request.agg` accepts `sum`, `mean`, or `count`; aggregation ignores missing revenues and empty sum/count are zero while empty mean is `None`. `request.window` is the trailing row width. Lookup yields `None` for unknown regions, missing/zero targets, or missing revenue. Region normalization is strip/lower. Input values are expected to follow the stated service schema.

Example:

```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

The implementations are imported from declared dependency `published.a01_r02`.
