# rowservices

Native Python implementations of the six row-table service families. Each public service has the API `family(rows, lookup, request)` and returns new dictionaries (input objects are not mutated). `lookup` and `request` are accepted by all adapters; unused arguments are ignored.

- `clean(rows, lookup, request)`: normalize region with strip/lower and fill missing units.
- `revenue(...)`: clean-style unit filling plus `revenue_cents`.
- `group(...)`: region groups and selected revenue aggregate.
- `monthly(...)`: month/region groups and selected revenue aggregate.
- `lookup(...)`: adds `revenue_cents_per_target` from region targets.
- `window(...)`: adds trailing row-window revenue mean.

Request keys: `fill` is `zero`, `mean`, or `median` (default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 (required in practice; absent values raise). Missing units are filled using nonmissing input units; all-missing yields zero. Group mean on no revenues is `None`; sum/count are zero. Rows with missing group keys are omitted. Lookup region keys are normalized with strip/lower as well; unknown/zero-target lookups yield `None`. Window averages nonmissing revenues within the trailing ROWS, including the current row. Revenue derivation yields `None` if either operand is missing. Original columns are retained by row services; group outputs contain only keys and aggregate.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 150}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 300
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 300}
]
```

Limitations: inputs are expected to have ordinary comparable numeric operands and string-or-null regions/dates as described by the service contract. Invalid fill/aggregate/window names raise `ValueError`.
