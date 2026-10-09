# Table transforms

Native Python implementation; no third-party dependencies. Public APIs are `clean(rows, request)`, and `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, `window(rows, lookup, request)`. Each returns new dicts and does not modify inputs. `clean` normalizes string regions with strip/lower and fills missing units according to `request['fill']` (`zero`, `mean`, or `median`, default zero). Revenue derives `revenue_cents`; grouped APIs accept `request['agg']` (`sum`, `mean`, `count`, default sum). Monthly groups by the first seven date characters and region. Lookup uses normalized region keys and adds revenue per target. Window uses trailing row count from `request['window']` (2, 3, or 4).

Example:

```python
from candidate import revenue, group
rows = [{'region':' East ', 'units':2, 'price_cents':50}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill':'zero','agg':'sum'}) == [
    {'region':'east', 'sum_revenue_cents':100}]
```

Missing region values remain `None`; grouping drops them. Revenue is `None` if either operand is missing. Mean of an empty set is `None`; sum/count of an empty group are zero (no empty groups are emitted). Inputs are expected to be mappings with numeric operands and ISO-like date strings; invalid fill/aggregation/window options raise `ValueError`.
