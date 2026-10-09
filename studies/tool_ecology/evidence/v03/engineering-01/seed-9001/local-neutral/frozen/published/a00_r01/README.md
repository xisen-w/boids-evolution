# Tabular service functions

Dependency-free native Python implementations. Public functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Their `serve_*` aliases are the publication adapters with the same arguments and results.

`rows` is a list of dictionaries. Functions return new lists and dictionaries, leaving inputs unchanged. Regions that are strings are stripped and lowercased. Missing units are filled using `request['fill']` (`zero`, `mean`, or `median`; default zero); all-missing units become zero. Revenue is units times price, or `None` if price is missing. Grouping accepts `request['agg']` (`sum`, `mean`, `count`; default sum), excludes missing grouping keys, counts nonmissing revenue, and sorts output keys lexically by their string representation. Monthly groups by the first seven date characters and region. Lookup adds `revenue_cents_per_target`; unmatched/missing/zero targets or missing revenue produce `None`. Window adds the trailing-row mean including current row; `request['window']` must be 2, 3, or 4 (default 2).

Example:

```python
from candidate import revenue
rows = [{'region': ' West ', 'units': None, 'price_cents': 25}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 0
```

The functions expect row dictionaries and a lookup iterable of dictionaries; malformed records and unsupported request options raise ordinary Python exceptions. Numeric values are not coerced.
