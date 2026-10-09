# Table service adapters

The package root exports six pure-Python callables. Each has signature `(rows, lookup, request)`, returns a fresh list/result, and does not mutate inputs. Rows are dictionaries and `lookup` is a list of region/target/manager dictionaries (used only by `lookup`).

* `clean(rows, lookup, request)`: normalize string regions using strip/lower; fill missing units and preserve all row fields/order.
* `revenue(rows, lookup, request)`: fill missing units, add `revenue_cents`, and preserve original region spelling and row order.
* `group(rows, lookup, request)`: normalize region, derive revenue, drop missing regions and aggregate nonmissing revenue.
* `monthly(rows, lookup, request)`: group by `date[:7]` and normalized region, dropping missing keys.
* `lookup(rows, lookup, request)`: normalize regions, derive revenue and append `revenue_cents_per_target`; target/manager are not added.
* `window(rows, lookup, request)`: derive revenue and append trailing-row `roll_revenue_cents` (region is not normalized).

`request` accepts `fill` (`zero`, `mean`, or `median`; default `zero`), `agg` (`sum`, `mean`, or `count`; default `sum`), and `window` (width; default 2). Even-sized medians average the middle pair; no observed units fills with zero. Revenue is `None` if price or units is missing. Group aggregation ignores missing revenues; empty sum/count are zero and empty mean is `None`. Group results sort by stringified keys. Lookup uses exact normalized region matching and returns `None` for unknown/missing/zero target or missing revenue. Window means nonmissing revenue values in the trailing ROWS slice, including current; an empty slice yields `None`.

Example:

```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Inputs are expected to follow the service schema (including ISO date strings); values and request options are not otherwise validated. Implementations are re-exported from the declared `published.a01_r02` dependency.
