# Row-table service adapters

Dependency: `published.a04_r01` (bundled declared dependency). Import this package as `candidate`.
All six public functions have signature `(rows, lookup, request)` and return new row lists without mutating inputs.

- `clean`: normalize region with strip/lower and fill missing units (`fill`: zero/mean/median; all missing -> 0).
- `revenue`: fill units and append `revenue_cents`; unlike clean and the derived aggregate families, this service preserves the input region verbatim. Revenue is `None` if units or price is missing.
- `group`: normalized-region groups; `agg` sum/mean/count over nonmissing revenue.
- `monthly`: normalized region and `date[:7]` groups, dropping missing grouping keys.
- `lookup`: normalized region target lookup; adds only `revenue_cents_per_target`.
- `window`: trailing ROWS average over nonmissing revenue, with `window` defaulting to 2.

Example:
```python
from candidate import revenue
revenue([{'region':' North ','units':2,'price_cents':50}], [], {'fill':'zero'})
# [{'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```
Dates are expected as strings for monthly's first-seven-character month extraction. Unknown fill falls back to zero; aggregate operations use the documented sum/mean/count values.
