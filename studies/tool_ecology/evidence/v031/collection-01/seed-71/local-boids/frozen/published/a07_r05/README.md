# Tabular service dispatch

A small named dispatcher and lazy job iterator over six pure row-table services. Implementations are reused from `published.a07_r02`.

## API

- `process(family, rows, lookup, request)` runs `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`; unknown names raise `ValueError`.
- `process_many(jobs)` returns a list of outputs for ordered four-item jobs `(family, rows, lookup, request)`.
- `process_iter(jobs)` returns a lazy iterator over those job outputs. Errors propagate when the corresponding item is requested.
- Root service adapters `clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, and `window_adapter` each accept `(rows, lookup, request)`.

```python
from candidate import process, process_iter
rows = [{'region': 'West', 'units': 2, 'price_cents': 50}]
assert process('revenue', rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
jobs = [('clean', rows, [], {'fill': 'zero'}),
        ('window', rows, [], {'fill': 'zero', 'window': 2})]
first = next(process_iter(jobs))
```

Rows are lists of mappings. Services normalize region via strip/lower where specified; fill units with zero/mean/median (all-missing becomes zero); derive revenue with missing operands producing `None`; group/monthly drop missing keys and aggregate nonmissing revenue; lookup returns null for absent/zero targets; windows are trailing ROWS windows. Output shape, sorting, and column preservation follow the underlying service. No schema coercion or error recovery is added.
