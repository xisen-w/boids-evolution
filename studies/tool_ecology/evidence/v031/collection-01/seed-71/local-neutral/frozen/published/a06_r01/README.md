# a06_r01

Native Python implementations of all six table service families. Public APIs are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup_revenue(rows, lookup, request)`, and `window(rows, lookup, request)`.
Inputs are lists of dictionaries; `lookup` is used only by `lookup_revenue`.
The `clean_service`, `revenue_service`, `group_service`, `monthly_service`,
`lookup_service`, and `window_service` names are equivalent three-argument
service adapters.

Example:

```python
from candidate import group
rows = [dict(region=" West ", date="2025-01-02", units=2,
             price_cents=150, id=1, product="x", cost_cents=50)]
assert group(rows, [], {"fill": "zero", "agg": "sum"}) == [
    {"region": "west", "sum_revenue_cents": 300}]
```

Missing values are represented by `None`. Fill defaults to zero and accepts
`zero`, `mean`, or `median`; aggregation defaults to `sum` and accepts `sum`,
`mean`, or `count`. Window defaults to 2 and accepts 2, 3, or 4. Invalid
parameter values raise `ValueError`. Rows and request dictionaries are not
mutated. Region matching in lookup uses stripped, lowercase string keys. The
implementation assumes dates are ISO-like strings when present.
