# Native row-table services

The package exports six adapters, each accepting `(rows, lookup, request)` and returning a fresh list (with fresh row dictionaries for row-preserving services). Inputs are not mutated. Rows are expected to be dictionaries with the fields described by the service contract.

* `clean(rows, lookup, request)`: strip/lowercase regions and fill missing units from request `fill` (`zero`, `mean`, or `median`; all missing becomes zero). Preserves every column and order.
* `revenue(...)`: fill units and add `revenue_cents`; region is preserved verbatim.
* `group(...)`: normalized region and revenue, omit missing region keys, aggregate nonmissing revenue using `agg` (`sum`, `mean`, `count`), sorted by stringified region.
* `monthly(...)`: same preparation; group on nonmissing month (`date[:7]`) and normalized region; sorted by stringified keys.
* `lookup(...)`: normalized region and revenue plus `revenue_cents_per_target`, using exact normalized region match; unknown/zero/None target or missing revenue yields None. Does not append lookup fields.
* `window(...)`: revenue plus trailing `window`-row mean, including current row; missing revenues are excluded from the mean, but rows still occupy window positions. Region preserved verbatim.

Aggregates count only nonmissing revenues; empty sum/count produce zero and empty mean produces None. Example:

```python
from candidate import clean, group
rows = [{'region': ' West ', 'units': None, 'price_cents': 4}]
clean(rows, [], {'fill': 'zero'})
# [{'region': 'west', 'units': 0, 'price_cents': 4}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'west', 'sum_revenue_cents': 0}]
```

Limitations: numeric inputs and parameter choices must follow the contract; this implementation does not coerce values.
