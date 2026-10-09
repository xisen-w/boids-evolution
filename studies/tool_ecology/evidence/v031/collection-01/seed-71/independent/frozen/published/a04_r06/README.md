# Tabular services facade

Native Python facade over the received, service-tested `published.a04_r03` implementation; no third-party packages. Public functions take `(rows, lookup, request)`: `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window`. Root adapters `serve_clean`, `serve_revenue`, `serve_group`, `serve_monthly`, `serve_lookup`, and `serve_window` expose the same signatures for service runners. All calls return copied output and do not mutate inputs.

Example:
```python
from candidate import group, window
rows = [{'region': ' N ', 'date': '2025-01-02', 'units': 2, 'price_cents': 30}]
assert group(rows, [], {'agg': 'sum'}) == [{'region': 'n', 'sum_revenue_cents': 60}]
assert window(rows, [], {'fill': 'zero', 'window': 2})[0]['roll_revenue_cents'] == 60
```

`clean` normalizes string regions and fills units. `revenue` fills units and appends revenue while retaining region text. `group` and `monthly` normalize regions and aggregate revenue, dropping missing keys; monthly uses date's first seven characters. `lookup_service` normalizes regions and appends revenue per exact normalized lookup target, without adding lookup columns. `window` appends mean revenue across trailing positional rows. Fill choices are `zero`, `mean`, `median` (default zero; all missing becomes zero); aggregates are `sum`, `mean`, `count` (default sum, count ignores missing revenues); window sizes are 2, 3, or 4. Output aggregate keys sort lexically by string form; empty sum/count are zero and empty mean is `None`. Schema-conforming mappings and valid parameters are expected; malformed inputs are not coerced.
