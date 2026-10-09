# Row table services

Import the six callables with `from candidate import clean, revenue, group, monthly, lookup_service, window`. Every callable has the exact signature `(rows, lookup, request)`; rows and lookup are lists of dictionaries and request is a dictionary. Results are fresh lists/dictionaries; inputs are not mutated. The package uses the received, dependency-free implementation `published.a05_r03`.

* `clean`: preserve row/column order and normalize non-null region strings using strip/lower; fill null units according to `request['fill']` (`zero`, `mean`, `median`; default zero). All-null units fill as zero; even median averages central values.
* `revenue`: fill units as above and add `revenue_cents` (`None` if units or price is missing); original columns remain.
* `group`: normalized region and revenue; omit null region keys; aggregate non-null revenues using `request['agg']` (`sum`, `mean`, `count`; default sum). Output `{region, <agg>_revenue_cents}`, sorted by stringified region. Empty aggregates are zero for sum/count and None for mean.
* `monthly`: same derivation and aggregation, grouped on non-null `date[:7]` and region, sorted by stringified month then region. Output month, region, aggregate field.
* `lookup_service`: normalized region/revenue and add `revenue_cents_per_target` from exact normalized region lookup. Unknown/missing/zero target or missing revenue gives None; target and manager are not added.
* `window`: revenue and trailing `request['window']` row mean (`2`, `3`, or `4`) of non-null revenue, including current row; None if the window contains no values.

Example:
```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 8}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 8, 'revenue_cents': 0}]
```
Invalid fill, aggregation, or window values raise ValueError. Dates are expected as ISO strings when present.
