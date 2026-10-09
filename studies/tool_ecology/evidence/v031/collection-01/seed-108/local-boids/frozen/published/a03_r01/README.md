# Row services

Native Python, no third-party dependencies. Public API consists of `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` in package `candidate`. Every call returns newly-created dictionaries and leaves arguments unmodified. Each takes rows as list of mappings and request as a mapping. `fill` is `zero`, `mean`, or `median` (default zero); all-missing units fill with zero. Aggregate `agg` is `sum`, `mean`, or `count` (default sum). Window size defaults to 2.

Example:
```python
from candidate import revenue, group
rows = [{'id': 1, 'region': ' West ', 'units': 2, 'price_cents': 125}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 250
group(rows, [], {'fill':'zero', 'agg':'sum'}) # [{'region':'west','sum_revenue_cents':250}]
```

Region strings are stripped and lowercased. Revenue services preserve input column order and append derived columns; grouped services omit missing region (and missing month for monthly) and sort keys by their string form. Lookup uses exact normalized region keys; duplicate lookup keys resolve to the last row. Window is a trailing physical-row window including the current row. Invalid fill/aggregate names raise `ValueError`. Inputs are expected to follow the documented table schema; date strings are sliced to their first seven characters.
