# Row-table services

Native Python, non-mutating implementations. Each public adapter accepts `rows, lookup, request` and returns new dictionaries (except grouped outputs, which have only the documented aggregate fields). Original row keys and order are retained in row-oriented services; new derived keys are appended.

- `clean(rows, lookup, request)`: normalize region by strip/lower and fill missing units.
- `revenue(rows, lookup, request)`: fill units and derive `revenue_cents`; does not normalize region.
- `group(rows, lookup, request)`: normalize region, derive revenue, and group by nonmissing region.
- `monthly(rows, lookup, request)`: normalize region, derive revenue, add `month` from date prefix and group by nonmissing month and region.
- `lookup(rows, lookup, request)`: normalize region, derive revenue and `revenue_cents_per_target`; does not add target or manager.
- `window(rows, lookup, request)`: derive revenue and trailing physical-row `roll_revenue_cents` mean; does not normalize region.

Fill is selected by `request['fill']` (`zero`, `mean`, `median`; default `zero`); all-missing units fill with zero. Aggregation is `request['agg']` (`sum`, `mean`, `count`; default `sum`). Count ignores missing revenue; empty sum/count are zero and empty mean is None. Window uses `request['window']` (default 2). Lookup uses exact normalized region matching; absent/zero targets or missing revenue produce None. Duplicate normalized lookup keys use the last entry. Rows and request are not mutated.

```python
from candidate import revenue, group
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 100
# group(rows, [], {'agg': 'sum'}) -> [{'region': 'north', 'sum_revenue_cents': 100}]
```

Inputs are expected to be dictionaries with numeric arithmetic fields and ISO-like date strings. Invalid fill/aggregation options raise ValueError. Window widths are positive integers.
