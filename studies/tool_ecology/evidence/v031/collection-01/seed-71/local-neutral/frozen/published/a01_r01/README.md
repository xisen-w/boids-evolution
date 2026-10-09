# Tabular service adapters

Native Python, no third-party dependencies. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each accepts the service's row dictionaries, lookup records, and request dictionary, returning a new list without modifying inputs.

```python
from candidate import revenue, group
rows = [{'id': 1, 'region': ' West ', 'units': None, 'price_cents': 25}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 0
# group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Region strings are stripped and lowercased. Fill supports `zero`, `mean`, and `median` (empty values fill with zero); aggregate supports `sum`, `mean`, and `count`. Group/monthly omit missing group keys; count includes only nonmissing revenues. Lookup uses normalized region keys, excludes manager/target columns, and yields `None` for missing/zero targets or missing revenue. Window accepts sizes 2, 3, or 4 and uses physical trailing rows including the current row. Derived outputs preserve source key order and append fields; clean preserves fields while normalizing/filling. Invalid parameter values raise `ValueError`.
