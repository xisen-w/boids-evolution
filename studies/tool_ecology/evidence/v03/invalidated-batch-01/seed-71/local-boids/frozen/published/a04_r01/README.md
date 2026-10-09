# Native table services

Import from `candidate` (or use the package as published). Each public adapter has signature `(rows, lookup, request)` and returns a new list of dictionaries without mutating inputs:

- `clean(rows, lookup, request)`: normalize region by stripping and lowercasing; fill missing units according to `request['fill']` (`zero`, `mean`, or `median`; default `zero`).
- `revenue(...)`: same fill and normalization, appending `revenue_cents` (units times price, or `None` if either is missing).
- `group(...)`: group derived revenue by nonmissing normalized region; `request['agg']` is `sum`, `mean`, or `count` (default `sum`).
- `monthly(...)`: group by nonmissing month (`date[:7]`) and region using the same aggregation options.
- `lookup(...)`: appends `revenue_cents_per_target` using normalized exact region keys from the lookup rows. Missing revenue, missing/zero target, or unknown key yields `None`.
- `window(...)`: appends trailing-row mean revenue; `request['window']` must be 2, 3, or 4. Null revenues are omitted from the mean but still occupy their row positions.

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 20}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
All original columns are retained in input order, with derived columns appended; aggregate outputs use the documented aggregate column names and sorted keys. Inputs are expected to be lists of dictionaries with the fields stated by the service contract. Unsupported fill/aggregation/window values raise `ValueError`.
