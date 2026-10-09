# Native table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each public service has the signature `(rows, lookup, request)` and returns a new list of dictionaries without mutating its arguments. `rows` contains row dictionaries; `lookup` is the lookup table (used only by `lookup`); `request` controls fill (`zero`, `mean`, `median`), aggregation (`sum`, `mean`, `count`), or rolling width (`2`, `3`, `4`).

`clean` normalizes region with strip/lower and fills missing units. `revenue` fills units and adds `revenue_cents` without normalizing region. Group and monthly normalize region and aggregate nonmissing revenue, dropping missing keys. `lookup` normalizes region and adds revenue divided by the exact normalized-region target; unknown, zero, missing targets and missing revenue yield `None`. `window` adds the trailing row-window mean of nonmissing revenue and does not normalize region. Original keys and order are retained for row-wise services.

Example:

```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 125, 'region': 'East'}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Empty group aggregations follow standard service semantics (sum/count zero, mean `None`). Values are expected to be numeric when present, regions strings or `None`, and dates ISO strings or `None`.
