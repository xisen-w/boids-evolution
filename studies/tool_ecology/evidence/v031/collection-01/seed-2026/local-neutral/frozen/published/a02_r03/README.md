# Row services

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Arguments
are a list of row dictionaries, optional list of lookup dictionaries, and a
request dictionary. Each call returns new dictionaries and leaves inputs alone.

`clean` normalizes region with strip/lower and fills null units. `revenue`
additionally derives `revenue_cents`. `group` and `monthly` aggregate non-null
revenue and return sorted summaries. `lookup` derives revenue per target;
`window` adds trailing row-window revenue means. Request keys are `fill`
(`zero`, `mean`, `median`; defaults to zero), `agg` (`sum`, `mean`, `count`;
defaults to sum), and `window` (2, 3, or 4; required for window).

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
```

Limitations: inputs are expected to follow the service schema; unsupported
fill/aggregation modes and invalid window widths raise `ValueError`. This
package delegates implementation to its declared dependency `a04_r01`.
