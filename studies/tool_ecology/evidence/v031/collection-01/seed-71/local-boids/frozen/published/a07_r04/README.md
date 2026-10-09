# Tabular service dispatch

This package provides named and ordered batch dispatch over six pure row-table services, reusing the tested implementation in `published.a07_r02`.

## Public API

`process(family, rows, lookup, request)` runs one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`. Unknown names raise `ValueError`.

`process_many(jobs)` accepts an iterable of four-item tuples `(family, rows, lookup, request)` and returns outputs in the same order. Processing stops and propagates an exception if any job is invalid.

The six service adapters `clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, and `window_adapter` each accept `(rows, lookup, request)`.

```python
from candidate import process, process_many
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert process('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
results = process_many([('clean', rows, [], {'fill': 'zero'}),
                        ('window', rows, [], {'fill': 'zero', 'window': 2})])
```

## Service behavior and limitations

Rows are lists of mappings. `clean` normalizes region strings using strip/lower and fills missing units (`zero`, `mean`, or `median`, all-missing to zero). `revenue` fills units and appends `revenue_cents`, null when either operand is missing. `group` and `monthly` normalize keys and aggregate nonmissing revenue using `sum`, `mean`, or `count`; missing group keys are dropped and outputs sorted by stringified keys. `lookup` normalizes region and appends per-target revenue; unknown/missing/zero targets yield null and lookup metadata is not added. `window` appends the mean of nonmissing revenue in each trailing row window (window size 2, 3, or 4). These transformations preserve input data and follow the received implementation's option defaults and validation. This API does not add schema coercion or error recovery.
