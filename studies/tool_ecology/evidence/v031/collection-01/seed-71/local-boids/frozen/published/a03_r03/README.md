# Tabular row service adapters

This package exposes six pure row-table adapters, reusing the verified native implementation in `a07_r02`.

Each public callable has signature `(rows, lookup, request)` and returns a fresh list of dictionaries; inputs are not mutated.

* `clean`: normalize string regions with strip/lower and fill missing units using `request['fill']` (`zero`, `mean`, `median`; all-missing becomes zero). Preserves columns/order.
* `revenue`: fill units and append `revenue_cents` (`None` when units or price is missing); preserves columns/order.
* `group`: normalized region, filled units and revenue; drops missing regions and groups nonmissing revenue using `request['agg']` (`sum`, `mean`, `count`).
* `monthly`: same revenue processing, grouped by month and normalized region; drops rows missing either key.
* `lookup`: normalized region and revenue plus `revenue_cents_per_target`; unknown region, missing/zero target or missing revenue gives `None`.
* `window`: revenue plus trailing-rows mean `roll_revenue_cents`, ignoring missing revenue values.

Aggregated outputs are sorted by stringified keys. Group count counts only nonmissing revenues. Lookup does not add target/manager columns. Example:

```python
from candidate import revenue
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Input is expected to be a list of mappings with the service's documented fields. Invalid fill, aggregate, or window values raise `ValueError`; window must be 2, 3, or 4.
