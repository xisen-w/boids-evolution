# Native tabular services

Public functions are `clean(rows, lookup_rows, request)`, `revenue(rows, lookup_rows, request)`, `group(rows, lookup_rows, request)`, `monthly(rows, lookup_rows, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`. Each accepts a list of dictionaries and returns fresh dictionaries without mutating inputs. `lookup_rows` is used only by `lookup`.

`request.fill` accepts `zero`, `mean`, or `median` (default `zero`); absent units are filled, and an entirely missing units column is filled with zero. `request.agg` accepts `sum`, `mean`, or `count` (default `sum`). Groups omit missing keys; counts count nonmissing revenue. Monthly groups use the first seven characters of date. `request.window` is 2, 3, or 4 for trailing ROWS including current. Region normalization is strip/lower in clean, group, monthly, and lookup; revenue and window retain the input region. Lookup region keys are normalized likewise. Derived revenue is `None` if units or price is missing.

Example:

```python
from candidate import revenue
rows = [{'region': ' East ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert rows[0]['region'] == ' East '  # original untouched
```

Inputs are expected to be mappings with values from the described service schema; invalid fill/aggregation/window options raise `ValueError` (window must be specified as 2, 3, or 4).
