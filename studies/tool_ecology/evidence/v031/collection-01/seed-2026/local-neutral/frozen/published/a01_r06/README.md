# Row services

Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes a list of row dictionaries, a lookup-table list (or `None`), and a request dictionary, and returns a fresh list. Implementation is delegated to the received pure-Python `published.a04_r04` implementation.

`clean` normalizes regions using strip/lower and fills missing units. `revenue` fills units and adds revenue cents, null when units or price are missing. `group` aggregates revenue by normalized region; `monthly` groups by month and region; both drop missing group keys. `lookup` adds revenue per target from exact normalized region keys without adding lookup metadata. `window` adds a trailing-ROWS mean including the current row. Existing row columns and order are preserved for row-oriented services.

Options: `fill` is `zero`, `mean`, or `median` (default `zero`; all-missing fills zero; even median averages central values); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 and is required for the window service. Group count counts nonmissing revenues. Empty sum/count values are zero; empty mean is `None`. Invalid option values raise `ValueError`.

Example:
```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 125}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 250
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 250}]
```
Inputs are expected to follow the specified row schema and types; no schema validation is promised.
