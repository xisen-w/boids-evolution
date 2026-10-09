# Table transformations

Native Python adapters: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Inputs are lists of dictionaries and are not mutated; returned row data preserve original columns and order where applicable.

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'mean'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```

`clean` normalizes regions by strip/lower and fills missing units. `revenue` adds revenue (None if price is missing). `group` and `monthly` normalize regions, drop missing group keys, and aggregate nonmissing revenue (`sum`, `mean`, or `count`). `lookup` normalizes row regions and adds revenue-per-target using lookup region keys; unknown/missing/zero target or missing revenue gives None. `window` adds the mean of nonmissing revenue in the trailing request.window rows (2, 3, or 4), including current row. Fill is `zero`, `mean`, or `median`, with all-missing units filled as zero. Mean of an empty group is None; sum/count are zero. Inputs are expected to follow the documented numeric/string table contract; invalid option values raise ValueError.
