# table_services

Pure-Python table services. Each public function accepts `(rows, lookup, request)` and returns fresh dictionaries/lists without mutating inputs. `clean` normalizes region with strip/lower and imputes missing units. `revenue` additionally appends `revenue_cents`. `group` and `monthly` return grouped aggregate records using `request['agg']` (`sum`, `mean`, `count`); missing keys are omitted. `lookup` appends revenue per exact normalized region target (manager is not returned). `window` appends the mean over the trailing `request['window']` rows.

`request['fill']` may be `zero`, `mean`, or `median`; an all-missing units column fills with zero. Revenue is null when either operand is null. Group means of empty non-null revenue sets are null; empty sums/counts are zero. Example:

```python
from candidate import revenue, group
rows = [{'region': ' West ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'west', 'sum_revenue_cents': 100}]
```

Input records are expected to use the documented table fields. Unknown aggregate/fill values fall back to sum/zero respectively. Dates are expected to be ISO date strings for monthly grouping.
