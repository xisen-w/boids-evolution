# Row services and dispatcher

Six pure row-table adapters are exported: `clean(rows, lookup, request)`,
`revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and
`window(rows, lookup, request)`. They provide region normalization/unit fill,
revenue derivation, grouping, monthly grouping, target lookup, and trailing-row
revenue means respectively. Fill modes are zero/mean/median; aggregate modes
sum/mean/count; window is a trailing ROWS window including current. Inputs are
not mutated. Full missing-value, output ordering, and aggregation semantics
follow `published.a06_r03`.

`run_service(family, rows, lookup_rows, request)` dispatches to an adapter by
family name and raises `KeyError` for unknown names. Example:

```python
from candidate import run_service
out = run_service("revenue", [{"units": 2, "price_cents": 50}], [], {"fill": "zero"})
assert out[0]["revenue_cents"] == 100
```

Requires `published.a06_r03` and its declared dependency `published.a06_r02`.
