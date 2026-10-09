# Tabular service adapters

Native Python implementations; no third-party dependencies. Public functions are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns
new dictionaries and does not mutate inputs. `rows` is a list of row dictionaries;
`request` supplies `fill` (`zero`, `mean`, `median`) for all services, `agg`
(`sum`, `mean`, `count`) for grouping, and `window` (2, 3, or 4) for rolling.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Region normalization is strip/lower. Missing units use the selected statistic
(all missing => zero); revenue is `None` if price or filled units is missing.
Group/monthly exclude missing keys and ignore missing revenue; empty sum/count
are zero, empty mean is `None`. Lookup uses normalized region keys and does not
add target/manager. Monthly expects ISO date strings (month is first seven chars).
The input contract specifies numeric values; invalid fill/aggregate/window options
raise `ValueError`.
