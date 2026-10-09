# Selective sales-view dispatcher

`run(rows, lookup_rows, request, families=None)` returns a dictionary keyed by family. With `families=None`, it computes all six services. Otherwise pass an iterable containing any of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`; only those services run. Unknown family names raise `ValueError`. Empty selection returns `{}`.

Each selected result follows the service semantics of the verified `published.a01_r01` implementation. Request fields are relevant to the selected service: `fill` for clean/revenue-derived services, `agg` for group/monthly, and `window` for window. Inputs are not mutated.

The six root adapters `clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, and `window_adapter` each have signature `(rows, lookup, request)` and return the corresponding full service output.

```python
from candidate import run
rows = [{'region': ' West ', 'date': '2025-03-01', 'units': 2, 'price_cents': 125}]
assert run(rows, [], {'fill': 'zero'}, ['revenue'])['revenue'][0]['revenue_cents'] == 250
```
