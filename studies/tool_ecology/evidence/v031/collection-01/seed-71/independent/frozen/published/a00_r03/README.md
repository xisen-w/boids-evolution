# Tabular service adapters

Native, non-mutating implementations for six row-table operations. Public API:
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`,
`monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and
`window(rows, lookup, request)`. Each accepts a list of dictionaries, lookup records, and a
request dictionary and returns new dictionaries (or grouped result dictionaries). Example:

```python
from candidate import monthly
monthly([{"region":" West ", "units":2, "price_cents":50,
          "date":"2025-03-02"}], [], {"fill":"zero", "agg":"sum"})
# [{'month': '2025-03', 'region': 'west', 'sum_revenue_cents': 100}]
```

Missing units use zero, mean, or median (all missing -> zero); revenues are null if a
product operand is missing. Group/monthly drop null keys. Aggregations are sum, mean, count;
empty means are null. Lookup normalizes region keys on both sides, and yields null for absent,
zero, or null targets. Window width is 2, 3, or 4 rows including current. Required input
fields are expected to have the documented scalar types; malformed dates/types are not
validated. Original row keys/order are retained for row-wise operations and inputs are not mutated.
