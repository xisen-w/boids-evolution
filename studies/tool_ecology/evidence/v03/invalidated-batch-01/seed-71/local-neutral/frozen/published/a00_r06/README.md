# Tabular service adapters

Native Python package exposing six service functions: `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. Each returns the corresponding contract output
as a fresh list of dictionaries. Implementations are reused from the declared,
verified dependency `published.a00_r05` (transitively `a00_r04`); no third-party
packages are required.

Inputs are row dictionaries, lookup dictionaries, and request dictionary.
Supported fill values are `zero`, `mean`, `median`; aggregations are `sum`,
`mean`, `count`; window lengths are 2, 3, and 4. Regions are normalized as
specified by the service contract. Functions do not mutate their inputs.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
Unsupported request options and malformed rows are outside the service contract.
