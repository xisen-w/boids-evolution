# Row-table services

Native Python adapters for six transformations, backed by `published.a06_r02`.

## API

`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)` accept a
list of dictionaries, lookup-record list, and request dictionary. They return
fresh output dictionaries and leave input containers/records unchanged.
`run(family, rows, lookup, request)` dispatches by one of the six names and
raises `ValueError` for an unsupported name.

Example:

```python
from candidate import run
out = run('group', rows, [], {'fill': 'zero', 'agg': 'sum'})
```

Fill options are `zero`, `mean`, and `median`; aggregation options are `sum`,
`mean`, and `count`; window widths are 2, 3, or 4. The services normalize
region for clean/group/monthly/lookup, derive revenue where applicable, and
implement their respective grouping, lookup, and trailing-row window output
semantics. Input rows are expected to follow the stated row schema and requests
to use supported options. This facade introduces no additional semantics.
