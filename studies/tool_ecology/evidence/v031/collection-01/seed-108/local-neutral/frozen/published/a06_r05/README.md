# Sales table transformations

Native Python package; no third-party dependencies. Each public operation accepts `(rows, lookup, request)` where rows and lookup are lists of dictionaries and request is a dictionary. Inputs are not mutated; outputs are newly allocated.

* `clean(rows, lookup, request)`: normalize region with strip/lower and fill missing units according to `request['fill']` (`zero`, `mean`, `median`; default zero; all missing becomes zero). Preserves fields and order.
* `revenue(...)`: fill units, append `revenue_cents`; it is `None` when units or price is missing.
* `group(...)`: normalized region revenue aggregation; supports `request['agg']` sum/mean/count (default sum), drops missing regions and sorts by stringified region.
* `monthly(...)`: as group, grouping on month (`date[:7]`) and region, dropping missing keys.
* `lookup_service(...)` (also `lookup`): append revenue and `revenue_cents_per_target`, using exact normalized region matching. Missing/zero target or missing revenue produces None.
* `window(...)`: append `roll_revenue_cents`, mean of nonmissing revenues in trailing `request['window']` rows including current (default 2).

Aggregation ignores missing revenue; empty sum/count are zero and empty mean is None. Example:

```python
from candidate import group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Expected input columns are ordinary Python scalar values as described by the service contract; dates are ISO strings. Lookup keys are normalized using the same region normalization.
