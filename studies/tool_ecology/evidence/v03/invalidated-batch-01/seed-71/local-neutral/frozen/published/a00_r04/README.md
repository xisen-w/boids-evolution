# Tabular service adapters (a00_r04)

Native Python convenience distribution exposing six service callables. The
implementation is reused directly from the declared dependency `a00_r03`.

Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup,
request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each
returns a new list of dictionaries; inputs are not mutated. The service
contract supports `request.fill` values `zero`, `mean`, `median`, `request.agg`
values `sum`, `mean`, `count`, and window sizes 2, 3, or 4.

`clean` normalizes region and fills missing units. `revenue` additionally
creates revenue cents. `group` aggregates by normalized region; `monthly`
aggregates by month and normalized region. `lookup` adds revenue per target
using normalized region keys. `window` adds trailing row-window revenue mean.
See dependency `published.a00_r03` for full semantics and limitations.

Example:
```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
