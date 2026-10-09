# Tabular transformation adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each accepts a list of mapping rows, a list of lookup mappings, and a mapping request, and returns a new list of dictionaries. Inputs are not mutated. Implementations are provided by the received, DEV-verified `published.a06_r02` dependency.

Rows conventionally contain `region`, `units`, `price_cents`, and (for monthly grouping) `date`; lookup records contain `region` and `target`. `request.fill` is `zero`, `mean`, or `median` (default `zero`, all missing fills as 0); `request.agg` is `sum`, `mean`, or `count` (default `sum`); `request.window` is a positive integer trailing ROWS width (default 2). Clean normalizes region and fills units. Revenue fills units and appends revenue while preserving region text. Group/monthly normalize region and aggregate nonmissing revenue, omitting null keys. Lookup normalizes region, adds per-target revenue, and leaves it null for missing/zero targets or missing revenue. Window adds a trailing mean over nonmissing revenue values in the row window. Other original fields are retained by row-oriented services.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': None, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})
# [{'region': ' North ', 'units': 0, 'price_cents': 50, 'revenue_cents': 0}]
group(rows, [], {'fill': 'zero', 'agg': 'sum'})
# [{'region': 'north', 'sum_revenue_cents': 0}]
```

Limitations: records must be mappings with appropriate schema keys; malformed non-mapping values are unsupported. Invalid fill/aggregation choices and nonpositive window sizes raise `ValueError`.
