# Row-table services

All service adapters accept `(rows, lookup, request)` and return new row dictionaries (or grouped dictionaries), without mutating inputs. `clean`, `revenue`, `group`, `monthly`, and `window` use the compatible native implementations in `published.a00_r01`. `lookup` is implemented here to normalize both sides of its region-key join.

```python
from candidate import clean, revenue, group, monthly, lookup, window
clean(rows, [], {'fill': 'median'})
lookup(rows, [{'region': ' West ', 'target': 10, 'manager': 'A'}], {'fill': 'zero'})
```

Fill supports zero/mean/median (all missing becomes zero); aggregation supports sum/mean/count. Group and monthly drop missing grouping keys. Lookup appends `revenue_cents_per_target`; unknown, zero, or missing target and missing revenue produce `None`. The package expects schema-conforming dictionaries and numeric operands.
