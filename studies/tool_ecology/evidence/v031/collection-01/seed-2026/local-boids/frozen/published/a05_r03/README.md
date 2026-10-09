# Tabular adapters

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each callable accepts `(rows, lookup, request)` and returns fresh dictionaries without mutating inputs. `clean` normalizes region (strip/lower) and fills units; `revenue` additionally appends `revenue_cents` (None if an operand is missing); group and monthly return aggregate records, dropping null grouping keys; lookup appends `revenue_cents_per_target`; window appends `roll_revenue_cents`.

`request.fill` supports `zero`, `mean`, `median` (all-missing becomes zero; even median averages middle values). `request.agg` supports `sum`, `mean`, `count`; count excludes missing revenue, and empty sum/count are zero while empty mean is None. `request.window` is trailing ROWS width 2, 3, or 4, including current. Aggregates sort keys lexically by string form. Lookup matches normalized region keys; unknown/missing/zero target or missing revenue gives None. No lookup metadata is added.

Example:
```python
from candidate import revenue
revenue([{'region': ' North ', 'units': 2, 'price_cents': 30}], [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
```
