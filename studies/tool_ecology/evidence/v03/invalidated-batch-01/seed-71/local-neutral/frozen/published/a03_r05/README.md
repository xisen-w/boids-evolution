# Row-table analytics

Native-Python adapters exposed at package root: `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. They return new dictionaries and do not mutate
inputs. They implement region normalization, unit filling, revenue derivation,
aggregation, exact normalized-region target lookup, and trailing physical-row
revenue means respectively. `clean` preserves columns; revenue-derived adapters
preserve existing columns and append derived columns.

Request options: `fill` is `zero`, `mean`, or `median` (default `zero`);
all-missing units fill with zero and even-sized medians average their middle
values. `agg` is `sum`, `mean`, or `count` (default `sum`); count excludes
missing revenue. `window` is a positive integer (default 2) counting rows,
including the current row. Grouped services drop missing keys; empty sum/count
are zero and empty mean is `None`. Unknown/zero targets and missing revenue
produce a `None` per-target result. Lookup does not add target or manager.

Example:
```python
from candidate import revenue
rows = [{'region': 'North', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```
Inputs are expected to have numeric units/prices and ISO-like date strings.
Invalid fill/aggregation options or nonpositive window widths are invalid.
