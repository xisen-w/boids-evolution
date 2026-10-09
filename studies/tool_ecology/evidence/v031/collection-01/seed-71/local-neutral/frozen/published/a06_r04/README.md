# Table services

Native Python facade, reusing the declared dependency `published.a06_r03`.
Every public service has signature `(rows, lookup, request)` and returns fresh
row dictionaries (or grouped output); input objects are not modified.

* `clean(rows, lookup, request)`: normalize region with strip/lower and fill
  missing units, preserving fields and order.
* `revenue(...)`: fill units and append `revenue_cents` (`None` if price is missing).
* `group(...)`: aggregate revenue by normalized nonmissing region.
* `monthly(...)`: aggregate by date's first seven characters and region, excluding
  missing keys.
* `lookup_revenue(...)`: append revenue and `revenue_cents_per_target`, using
  exact normalized region matching; unknown/zero/missing target yields `None`.
* `window(...)`: append rolling mean of nonmissing revenue across trailing rows.

`*_service` are root-level adapters with the same signature; `lookup_service`
adapts `lookup_revenue`. Request options: `fill` is `zero`, `mean`, or `median`
(default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window`
is 2, 3, or 4 (default 2). All-missing units fill with zero; median of an even
sample averages the middle pair. Group count counts nonmissing revenue. Empty
mean groups produce `None`; empty sum/count groups produce zero (no rows are
emitted for absent keys). Dates are expected to support `[:7]`.

Example:
```python
from candidate import revenue
revenue([{"units": 2, "price_cents": 50}], [], {"fill": "zero"})
# [{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
