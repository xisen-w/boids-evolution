# Table services

Dependency-free native Python functions: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns new dictionaries and does not mutate the arguments. `lookup` is the lookup-table argument (unused except by the lookup service).

* `clean`: normalize region by stripping and lowercasing strings; fill missing units using request `fill` (`zero`, `mean`, `median`; default `zero`). Preserves columns and order.
* `revenue`: fill missing units and append `revenue_cents` (`None` if units or price is missing); other columns retained in order, region unchanged.
* `group`: normalized region aggregate, omitting missing region; request `agg` is `sum`, `mean`, or `count` (default `sum`).
* `monthly`: normalize/derive revenue, group by nonmissing month and region; output sorted month/region and aggregate using `agg`.
* `lookup`: append `revenue_cents_per_target` using exact normalized region matching. Missing/zero target or missing revenue gives `None`.
* `window`: append `roll_revenue_cents`, the mean of nonmissing revenue in trailing `window` rows including current. `window` must be 2, 3, or 4.

Fill's all-missing case is zero; even-sized median uses the central-value average. Aggregation omits missing revenue, with empty sum/count equal to zero and empty mean `None`. Example:

```python
from candidate import revenue
revenue([{'units': None, 'price_cents': 4, 'region': ' X '}], [], {'fill': 'zero'})
# [{'units': 0, 'price_cents': 4, 'region': ' X ', 'revenue_cents': 0}]
```

Inputs are lists of dictionaries and supported request options must be supplied. Date month extraction uses the first seven characters of the date string.
