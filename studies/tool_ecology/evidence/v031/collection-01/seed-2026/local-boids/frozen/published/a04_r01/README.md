# Table service transforms

Native Python functions accept `(rows, lookup, request)`; inputs are not mutated. `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement the corresponding service transforms. Rows are dictionaries; outputs retain source key order and append derived keys. Regions are stripped/lowercased. Missing units are filled by `request['fill']` (`zero`, `mean`, or `median`, default `zero`; all missing becomes zero). Aggregations use `request['agg']` (`sum`, `mean`, or `count`, default `sum`). Window uses `request['window']` (2/3/4, default 2), counting rows including current.

Example:
```python
from candidate import revenue
rows = [{'region':' North ', 'units':None, 'price_cents':10}]
assert revenue(rows, [], {'fill':'zero'}) == [
    {'region':'north', 'units':0, 'price_cents':10, 'revenue_cents':0}]
```

Unknown aggregation/fill and unsupported window sizes raise `ValueError`. Lookup targets are keyed by normalized region; manager is not added. Lookup requires rows to have the ordinary service fields. Group outputs omit missing grouping keys and ignore missing revenue; empty sum/count are zero and empty mean is `None`.
