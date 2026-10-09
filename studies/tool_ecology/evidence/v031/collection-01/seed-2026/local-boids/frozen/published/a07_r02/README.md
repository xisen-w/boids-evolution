# Table service utilities

Pure-Python adapters for the six table service families. Import functions with `from candidate import clean, revenue, group, monthly, lookup, window`. Each accepts `(rows, lookup, request)`; inputs are copied, never mutated. Rows are dictionaries.

`clean` normalizes region via strip/lower and imputes missing units. `revenue` imputes and appends `revenue_cents` without normalizing region. `group` and `monthly` normalize region, derive revenue, and aggregate using request `agg` (`sum`, `mean`, `count`); monthly groups by the first seven date characters. `lookup` normalizes region and appends `revenue_cents_per_target` using normalized lookup keys. `window` derives revenue and appends the mean over trailing rows including current (`request.window` 2, 3, or 4).

All accept request `fill` (`zero`, `mean`, or `median`; default zero); all-missing units become zero. Example:
```python
from candidate import group
assert group([{'region':' West ', 'units':2, 'price_cents':50}], [],
             {'fill':'zero','agg':'sum'}) == [{'region':'west','sum_revenue_cents':100}]
```
Aggregations omit null revenue; empty sum/count are zero and empty mean is None. Unknown lookup keys and null/zero targets yield None. Expected input schema uses string dates and numeric units/prices/targets. Invalid fill, aggregation, or window values raise ValueError (invalid agg is checked when aggregating).
