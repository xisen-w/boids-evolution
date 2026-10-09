# Tabular service adapters

Native Python implementation of all six specified service families. Public APIs
are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each takes
list-of-dict input and returns a new list; input rows, lookup rows, and request
are not modified. Requests use `fill` (`zero`, `mean`, or `median`), `agg`
(`sum`, `mean`, or `count`), and `window` (2, 3, or 4) as relevant. Example:

```python
from candidate import clean, group
clean(rows, [], {"fill": "median"})
group(rows, [], {"fill": "zero", "agg": "sum"})
```

Clean normalizes string regions with strip/lower and fills missing units (an
all-missing column fills with zero). Revenue derives cents, with None if an
operand is missing. Group/monthly exclude missing keys; aggregates exclude
missing revenues. Lookup uses exact normalized region keys and returns None
for absent/zero targets. Window means nonmissing revenues in the trailing ROWS.
No validation of ISO date format or numeric types beyond the stated input
contract is performed. Empty groups do not occur in list-of-dict inputs.
