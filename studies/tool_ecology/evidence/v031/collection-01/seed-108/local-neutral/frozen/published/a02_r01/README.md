# Table services

Native Python implementation of the six specified table transformations. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes list-of-dict rows, a lookup-row list, and a request dict, and returns new dictionaries without mutating inputs. The lookup argument is unused except by the lookup service. Requests accept `fill` (`zero`, `mean`, `median`; default `zero`), `agg` (`sum`, `mean`, `count`; default `sum`), and `window` (2, 3, or 4).

Example:

```python
from candidate import revenue
rows = [{"region": " West ", "units": 2, "price_cents": 150}]
assert revenue(rows, [], {"fill": "zero"})[0]["revenue_cents"] == 300
```

Missing values are represented by `None`. Group/monthly results omit missing grouping keys; group aggregates ignore missing revenue. Region normalization is strip/lower for strings. The implementation expects the documented input fields and valid request parameter values; it does not interpret NaN as missing.
