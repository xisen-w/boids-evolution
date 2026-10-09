# Table service adapters

This package provides a convenient root namespace for six pure-Python adapters, re-exported unchanged from `published.a01_r02`. Every public callable has signature `(rows, lookup, request)` and returns a fresh result without mutating its inputs. Inputs are lists of row dictionaries; lookup rows are used only by `lookup`.

- `clean(rows, lookup, request)`: strip/lower region strings and fill missing units.
- `revenue(rows, lookup, request)`: fill missing units and add `revenue_cents`; preserves region values as provided.
- `group(rows, lookup, request)`: normalize region, calculate revenue and aggregate nonmissing revenue by region.
- `monthly(rows, lookup, request)`: group revenue by month (`date[:7]`) and normalized region.
- `lookup(rows, lookup, request)`: normalize region and add `revenue_cents_per_target` from an exact normalized region lookup.
- `window(rows, lookup, request)`: append trailing-row mean revenue `roll_revenue_cents`; region is preserved.

`request` supports `fill` = `zero`, `mean`, or `median` (default `zero`), `agg` = `sum`, `mean`, or `count` (default `sum`), and `window` as trailing ROWS width (default 2). All-missing units fill with zero. Revenue is `None` when price or units is missing. Grouping drops missing keys; empty sum/count are zero and empty mean is `None`. Lookup yields `None` for missing revenue, unknown region, or missing/zero target. Window averages nonmissing revenues within the row window only.

Example:

```python
from candidate import revenue
result = revenue([{'units': 2, 'price_cents': 50, 'region': 'West'}], [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 100
```

This namespace adds no transformation behavior: semantics, accepted values, and limitations are those of its declared `a01_r02` dependency. Dates are expected to be ISO `YYYY-MM-DD` strings; malformed inputs are not validated.
