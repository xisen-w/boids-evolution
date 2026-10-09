# Tabular service dispatcher

Native-Python adapters for six row-table operations, plus a name-based
`run` convenience API. Public calls take `(rows, lookup, request)` and return
new dictionaries/lists without changing inputs. The six operations follow the
service contract: clean normalizes region and fills units; revenue adds
revenue_cents; group and monthly aggregate; lookup adds revenue per target;
window computes a trailing-row mean. Parameters are supplied through request
(`fill`: zero/mean/median, `agg`: sum/mean/count, `window`: 2/3/4).

```python
from candidate import run, group
result = run('group', rows, [], {'fill': 'zero', 'agg': 'sum'})
# Equivalent to group(rows, [], {'fill': 'zero', 'agg': 'sum'})
```

`run(family, rows, lookup, request)` accepts exactly `clean`, `revenue`,
`group`, `monthly`, `lookup`, or `window`; an unrecognized family raises
ValueError. See service contract for output schemas and edge cases. Inputs are
expected to use the documented row/lookup schema; unrelated malformed field
types are not validated.
