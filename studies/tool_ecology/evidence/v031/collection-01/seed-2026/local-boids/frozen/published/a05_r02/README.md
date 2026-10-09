# Row-table service adapters

The package exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`.
Inputs are lists of dictionaries and request is a dictionary. Each adapter returns
new row dictionaries (or grouped result dictionaries) and leaves inputs untouched.

`request['fill']` accepts `zero`, `mean`, or `median`; missing units are filled
from the nonmissing input units, with all-missing data filled by zero. Grouped
services use `request['agg']` (`sum`, `mean`, or `count`). `window` uses
`request['window']` as a trailing number of rows (2, 3, or 4). Revenue is
`units * price_cents`, or `None` if either is missing. Region strings are
stripped and lowercased where required. Lookup keys are exact: a normalized row
region is matched to the lookup table's region key; rows with absent, zero-target,
or unknown targets receive `None` for per-target revenue.

```python
from candidate import revenue, lookup
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

No schema validation is performed. This package builds on the verified
`published.a00_r01` implementation for five service families.
