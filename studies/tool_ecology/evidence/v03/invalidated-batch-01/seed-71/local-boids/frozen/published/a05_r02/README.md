# Row-table service adapters

Dependency-backed adapters to the verified native implementation `published.a01_r01`.
Each public function has signature `(rows, lookup, request)` and returns the
family's output without mutating inputs:

* `clean(rows, lookup, request)` fills units and normalizes region.
* `revenue(...)` fills units and adds revenue_cents.
* `group(...)` groups by normalized region using request.agg.
* `monthly(...)` groups by month and normalized region.
* `lookup(...)` adds revenue_cents_per_target from exact normalized-region lookup.
* `window(...)` adds trailing-row mean revenue using request.window.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
Fill modes are zero/mean/median; aggregation modes sum/mean/count; window widths
are 2, 3, or 4. Missing operands yield null revenue. A missing/zero lookup target
yields null ratio. Input rows are expected to be dictionaries as specified by the
service contract; invalid parameters raise ValueError. `lookup` is a required
positional argument even for families that do not use it.
