# Tabular services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from `candidate`. Each takes `(rows, lookup, request)` and returns new dictionaries without mutating inputs. Missing data is `None`.

- `clean`: normalize region (strip/lower) and fill missing units.
- `revenue`: fill units and append `revenue_cents` (`None` if units or price is missing).
- `group` / `monthly`: normalize regions, compute revenue, then aggregate nonmissing revenues with request `agg` (`sum`, `mean`, `count`); monthly groups on first seven date characters too. Null keys are dropped, output sorted by stringified keys. Empty sum/count are zero; empty mean is None.
- `lookup`: normalize row region, derive revenue, append `revenue_cents_per_target`. The lookup table uses exact region keys; unknown/null/zero targets and null revenue yield None.
- `window`: derive revenue and append trailing row-window mean, including current row and ignoring missing revenues. Window must be 2, 3, or 4.

For fill policies `zero`, `mean`, and `median`, all-missing units fill with zero and even medians average the central values. Example:
```python
from candidate import revenue
revenue([{'region':' X ', 'units':None, 'price_cents':5}], [], {'fill':'zero'})
# [{'region': ' X ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}]
```
