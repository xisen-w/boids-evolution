# Table service transformations

Import `from candidate import clean, revenue, group, monthly, lookup, window`. Every public function accepts `(rows, lookup, request)`; `rows`/lookup are lists of dictionaries and inputs are not mutated. `request` accepts `fill` (`zero`, `mean`, `median`) for all functions, `agg` (`sum`, `mean`, `count`) for group/monthly, and `window` (row width) for window. Missing units are imputed from nonmissing units (empty -> zero); revenue is units times price and is null if either is null.

```python
from candidate import group
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
assert group(rows, [], {'fill':'zero','agg':'sum'}) == [
    {'region':'west','sum_revenue_cents':100}]
```

`clean` preserves all columns while normalizing region and filling units. `revenue` preserves columns and appends `revenue_cents`. `group` and `monthly` return aggregate records, dropping null group keys. `lookup` appends `revenue_cents_per_target` using normalized exact region keys (lookup keys are normalized likewise); missing/zero targets yield null. `window` appends the trailing-row mean, including current row and ignoring missing revenues. Inputs are expected to follow the service schema; aggregation names and fill names should be the listed values.
