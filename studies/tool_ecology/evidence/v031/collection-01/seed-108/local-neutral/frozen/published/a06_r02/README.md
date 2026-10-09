# Table service transformations

Pure native-Python functions taking `(rows, lookup, request)` and returning fresh dictionaries (inputs are not mutated). Rows and lookup are lists of mappings conforming to the service schema.

Public APIs: `clean`, `revenue`, `group`, `monthly`, `lookup_revenue`, and `window`; service-check aliases ending `_service` are also available at package root. `clean` normalizes string regions using strip/lower and fills missing units. `revenue` and `window` fill units and append `revenue_cents` / rolling mean respectively, preserving region spelling; missing price or units yields missing revenue. `group`, `monthly`, and `lookup_revenue` normalize regions as specified. Filling supports zero/mean/median and all missing units fill to zero. Aggregation supports sum/mean/count and skips missing revenue; empty sum/count are zero and empty mean is None. Lookup target matching uses normalized region; absent/zero targets produce None. Window uses trailing ROWS including current and averages nonmissing revenues.

Example:
```python
from candidate import revenue, clean
rows = [{'region': ' West ', 'units': None, 'price_cents': 50}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'west'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

Malformed schemas/requests are not validated. Date values are expected as ISO strings when using `monthly`.
