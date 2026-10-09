# Row-table services

Pure list-of-dictionary adapters re-exported from the tested `a03_r03` implementation.
Each function accepts `(rows, lookup, request)` and returns a fresh result without
mutating its inputs:

* `clean`: normalize regions by strip/lower; fill missing units by zero/mean/median.
* `revenue`: clean units and append revenue cents, or `None` if either operand is missing.
* `group`: aggregate revenue by normalized region, omitting missing regions.
* `monthly`: aggregate by date month and normalized region, omitting missing keys.
* `lookup`: add revenue per looked-up regional target (unknown/zero/missing yields `None`).
* `window`: add trailing-row rolling mean of nonmissing revenue.

Aggregation accepts sum/mean/count; ordering and empty groups follow the service
contract. Aggregated records sort lexically by stringified keys. Group count counts
nonmissing revenue. Lookup output does not include lookup metadata. Window accepts
2, 3, or 4. Example:

```python
from candidate import revenue
assert revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100
```

Inputs should have the documented service fields. Invalid fill, aggregation, or
window parameters raise `ValueError` in the underlying implementation.
