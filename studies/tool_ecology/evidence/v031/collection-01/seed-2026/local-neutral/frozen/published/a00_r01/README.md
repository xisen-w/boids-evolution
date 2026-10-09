# candidate

Pure-Python implementations of six tabular services. Public adapters all accept `(rows, lookup, request)`; rows and lookup are sequences of mappings and are never mutated. Results are fresh dictionaries.

* `clean(rows, lookup, request)` normalizes non-null regions with strip/lower and fills null units. `request['fill']` is `zero`, `mean`, or `median` (default `zero`); all-missing units fill with zero.
* `revenue(...)` performs clean behavior and appends `revenue_cents` (`units * price_cents`, or null if either is null).
* `group(...)` returns region aggregates, dropping null regions. `request['agg']` is `sum`, `mean`, or `count` (default `sum`); count excludes null revenue. Output column is `<agg>_revenue_cents`.
* `monthly(...)` groups on non-null month (`date[:7]`) and region, with the same aggregation semantics.
* `lookup_service(...)` appends `revenue_cents_per_target`, using exact normalized region keys. Missing/zero targets and missing revenue produce null. Lookup manager/target are not copied to output.
* `window(...)` appends `roll_revenue_cents`, a mean of non-null revenue values among trailing `request['window']` rows including current (2, 3, or 4; default 2).

Example:
```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```
Unknown fill/aggregation/window options raise `ValueError`. Original fields and insertion order are retained, with derived fields appended. Group outputs sort keys lexically by their string forms.
