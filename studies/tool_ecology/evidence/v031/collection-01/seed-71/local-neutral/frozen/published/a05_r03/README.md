# Table service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, lookup records (only used by lookup service), and request dictionary. Returns a newly transformed list; source rows are not mutated. Implementations are composed from `published.a04_r01` and `published.a01_r01`.

Example:
```python
from candidate import revenue
rows = [{'id': 1, 'region': ' West ', 'units': None, 'price_cents': 25}]
print(revenue(rows, [], {'fill': 'zero'})) # derived revenue_cents is 0
```

`clean` normalizes region/fills units; `revenue` adds revenue_cents; `group` and `monthly` aggregate; `lookup` adds per-target revenue; `window` adds trailing row-window mean. Fill options are zero/mean/median; aggregation options sum/mean/count. These adapters follow the service input schema and do not validate malformed schemas beyond underlying implementations.
