# Row-table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from
`candidate`. Each public function has the exact signature
`function(rows, lookup, request)` and returns a new list of dictionaries.
The package delegates to the native verified implementation
`published.a00_r01` (declared dependency `a00_r01`).

- `clean`: strip/lower regions and fill missing units.
- `revenue`: fill units and derive `revenue_cents` (null if either operand is null).
- `group`: aggregate non-null revenue by normalized region, dropping null keys.
- `monthly`: aggregate by month and normalized region, dropping null keys.
- `lookup`: append revenue per exact-region target; unavailable/zero targets yield null.
- `window`: append mean non-null revenue over trailing ROWS including current.

Fill modes are `zero`, `mean`, and `median` (all-missing becomes zero);
aggregation modes are `sum`, `mean`, and `count`. Request is passed unchanged;
`window` uses its requested window size. Example:

```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 30}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'units': 2, 'price_cents': 30, 'revenue_cents': 60}]
```

Inputs are expected to be list-of-dict rows and lookup entries, with supported
request parameters. Dates for monthly grouping are ISO date strings. Lookup
uses exact region keys. The adapter does not add target or manager columns.
