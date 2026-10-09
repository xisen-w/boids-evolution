# Region-target lookup enrichment

`candidate.lookup(rows, lookup_rows, request)` returns a new list of copied row dictionaries. It fills missing `units` from `request['fill']` (`zero`, `mean`, or `median`; default `zero`; all missing fills with zero), derives `revenue_cents = units * price_cents` (or `None` when price is missing), then adds `revenue_cents_per_target`.

Row region strings are stripped and lowercased before exact key matching against `lookup_rows[*]['region']`; lookup keys themselves are not normalized. Unknown regions and missing/zero targets produce a `None` rate. Original fields and row order are preserved; neither input nor request is mutated. Example:

```python
from candidate import lookup
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
assert lookup(rows, [{'region':'west','target':10}], {})[0]['revenue_cents_per_target'] == 10
```
