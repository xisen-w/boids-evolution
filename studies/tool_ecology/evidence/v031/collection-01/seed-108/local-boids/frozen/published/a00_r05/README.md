# Row service facade

Native-Python facade re-exporting the verified implementations in
`published.a00_r04`. Public call signatures are `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. Each returns a new list of output row dictionaries;
input tables and request are not intentionally modified.

Example:
```python
from candidate import revenue
rows = [{"region": " West ", "units": None, "price_cents": 12}]
assert revenue(rows, [], {"fill": "zero"})[0]["revenue_cents"] == 0
```

`clean` normalizes region and fills missing units; `revenue` adds revenue;
`group` and `monthly` aggregate; `lookup` adds per-target revenue; `window`
adds a trailing row-window mean. Fill choices are zero/mean/median (all-missing
uses zero), aggregate choices sum/mean/count, and window is supplied in the
request. Aggregations omit missing revenue and omit missing group keys. Exact
edge-case semantics are those of the declared dependency `a00_r04`. No
independent implementation is included.
