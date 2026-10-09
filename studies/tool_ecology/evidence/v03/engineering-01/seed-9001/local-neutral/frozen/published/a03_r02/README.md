# Table service adapters

`candidate` provides six functions, each taking `(rows, lookup, request)` and returning fresh row dictionaries (or grouped summaries) without mutating inputs:

- `clean`: normalizes non-null region strings using strip/lower and fills missing units.
- `revenue`: fills units and derives `revenue_cents`; region spelling is preserved.
- `group`: normalizes region and groups non-null regions, aggregating nonmissing revenue.
- `monthly`: groups normalized region and `date[:7]`, dropping missing keys.
- `lookup`: normalizes region and appends `revenue_cents_per_target`; unknown/missing/zero targets yield None.
- `window`: appends mean revenue over trailing ROWS, including current row.

Fill choices are `zero`, `mean`, or `median` (even median averages central values; all-missing becomes zero). Aggregations are `sum`, `mean`, or `count`; count counts nonmissing revenue. Empty sum/count groups yield zero and empty mean yields None. Window widths are 2, 3, or 4. Original row order and columns are retained for row-wise services; derived keys are appended. Group summaries sort keys lexically. Lookup metadata is not added to output.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' EAST ', 'product': 'x', 'date': '2025-01-02',
         'units': 2, 'price_cents': 50, 'cost_cents': 10}]
assert clean(rows, [], {'fill': 'zero'})[0]['region'] == 'east'
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'east', 'sum_revenue_cents': 100}]
```

This package depends on the published `a02_r01` implementation; inputs should follow the stated schema and valid request parameter choices.
