# Tabular service adapters

Exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. These
are thin adapters to the verified `published.a02_r04` services and preserve
their exact schemas and semantics. `lookup` here is the lookup-enrichment
service (its second argument is the lookup table).

`run_service(family, rows, lookup_rows, request)` dispatches one family by name;
unknown names raise `ValueError`. `run_many(jobs)` accepts an iterable of
four-tuples `(family, rows, lookup_rows, request)` and returns results in the
same order. Errors from a service propagate; inputs are not modified by this
package.

```python
from candidate import run_many
results = run_many([
    ("clean", rows, [], {"fill": "zero"}),
    ("revenue", rows, [], {"fill": "mean"}),
])
```

The six transformations, including required `fill`, `agg`, and `window`
parameters and output details, are documented by the underlying published
service package. This facade performs no validation or coercion.
