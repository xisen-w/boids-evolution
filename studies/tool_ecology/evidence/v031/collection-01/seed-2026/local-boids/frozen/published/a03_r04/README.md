# Row-table services

Root callables `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` implement the six row-table service families. Inputs are lists of dictionaries and are not mutated; row-producing services return copied rows preserving input order and columns. Grouped services return aggregate dictionaries.

`request.fill` is `zero`, `mean`, or `median` (default zero; all-missing fills with zero); `request.agg` is `sum`, `mean`, or `count` (default sum); `request.window` is 2, 3, or 4 (default 2). Regions are strip/lower normalized by clean, group, monthly, and lookup; revenue and window retain region values. Revenue is units times price or `None`; grouping drops null keys and ignores null revenues. Monthly uses the first seven date characters. Lookup appends `revenue_cents_per_target`; unknown/null region, missing/zero target, or missing revenue gives `None`.

Example:
```python
from candidate import clean, lookup
clean([{'region':' West ', 'units':None}], [], {'fill':'zero'})
lookup([{'region':' West ', 'units':2, 'price_cents':5}],
       [{'region':'west', 'target':10}], {'fill':'zero'})
```
Schema assumes numeric operands and ISO-like date strings. Duplicate lookup keys use the last row.
