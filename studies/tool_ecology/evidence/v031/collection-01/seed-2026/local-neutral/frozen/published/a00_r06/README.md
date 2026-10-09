# Sales table services

The package root exports `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns a new list of dictionaries and does not mutate arguments. This package re-exports implementations from `published.a00_r05` (which depends on the verified native implementation `a00_r04`).

`clean` normalizes region using strip/lower and fills missing units according to `request['fill']` (`zero`, `mean`, or `median`; all missing becomes zero, even median averages middle values). `revenue` adds `revenue_cents`, None if units or price is missing. `group` aggregates nonmissing revenue by normalized region; `monthly` groups by date prefix and region. Both use `request['agg']` (`sum`, `mean`, `count`), omit missing grouping keys and sort by stringified keys. Empty sum/count are zero, empty mean None. `lookup` adds `revenue_cents_per_target` based on exact normalized region lookup; unknown/missing/zero target produces None. `window` adds trailing ROWS mean `roll_revenue_cents`, using `request['window']` and ignoring missing revenue values (None when the window has none).

Example:
```python
from candidate import revenue
rows = [{'region': ' WEST ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Inputs should conform to the documented row/lookup/request contract; the adapters do not perform schema validation.
