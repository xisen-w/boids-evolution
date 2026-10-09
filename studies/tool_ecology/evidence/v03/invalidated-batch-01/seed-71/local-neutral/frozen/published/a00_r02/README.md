# Tabular services

Pure Python public adapters `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` each take `(rows, lookup, request)` and return new data without mutating inputs. Fill choices are zero/mean/median; all-missing units become zero. Aggregations are sum/mean/count; count counts nonmissing revenues. Window is a trailing 2/3/4 row window inclusive of current. Clean/group/monthly/lookup normalize region strings; revenue and window preserve region. Revenue is null if units or price are missing. Group services drop missing keys; lookup returns null on missing/zero targets.

Example:
```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 100
```
