# Row services (a07_r03)

This package re-exports the tested pure-Python API from `published.a07_r02`.
Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from
`candidate`. Each callable accepts `(rows, lookup, request)` and returns a
new list without mutating its inputs. Rows and lookup are lists of mappings;
request is a mapping.

Example:
```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

`clean` normalizes regions and fills missing units. `revenue` fills units and
derives revenue; group/monthly aggregate nonmissing revenue; lookup adds the
region target ratio; window adds a trailing ROWS mean. Fill is zero/mean/median
(all-missing becomes zero); aggregation is sum/mean/count; window is 2, 3, or
4. Revenue is `None` if units or price is missing. The implementation assumes
numeric operands and ISO-like dates; invalid parameters may raise `ValueError`.
