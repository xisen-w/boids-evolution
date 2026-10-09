# Table service entry points

This package provides the six table transformation functions through a small stable namespace and reuses the verified dependency `published.a07_r02` (no separate transformation implementation).

Each callable accepts `(rows, lookup, request)` and returns new dictionaries without mutating inputs:

* `clean`: normalize region strings and fill missing units.
* `revenue`: fill units and append `revenue_cents`.
* `group`: normalized region revenue aggregate.
* `monthly`: month-and-region aggregate.
* `lookup_service`: append revenue per exact normalized region target.
* `window`: append trailing row-window mean.

Fill modes are zero/mean/median; aggregate modes are sum/mean/count. All-missing units fill as zero; grouping excludes missing keys; missing revenue is excluded from aggregation. Window widths 2, 3, and 4 are supported. For example:

```python
from candidate import group
result = group([{'region': ' West ', 'units': 2, 'price_cents': 50}], [],
               {'fill': 'zero', 'agg': 'sum'})
assert result == [{'region': 'west', 'sum_revenue_cents': 100}]
```

The input contract is list-of-dictionaries and lookup rows with region/target fields. This package intentionally delegates semantics to its declared dependency rather than implementing additional behavior.
