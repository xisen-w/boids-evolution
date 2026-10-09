# Tabular service functions

Dependency-free Python functions, each with the exact public signature
`function(rows, lookup, request)`. Inputs are lists of mapping-like row dictionaries;
functions return fresh dictionaries/lists and do not mutate inputs. `lookup` is
used only by the lookup service. Missing numeric values are represented by `None`.

```python
from candidate import clean, revenue, group, monthly, lookup, window
rows = [{'id': 1, 'region': ' West ', 'product': 'x', 'date': '2024-01-02',
         'units': None, 'price_cents': 250, 'cost_cents': 100}]
clean(rows, [], {'fill': 'zero'})
# [{'id': 1, 'region': 'west', 'product': 'x', 'date': '2024-01-02',
#   'units': 0, 'price_cents': 250, 'cost_cents': 100}]
revenue(rows, [], {'fill': 'zero'})  # appends revenue_cents=0; region unchanged
```

`clean` normalizes region by stripping and lowercasing and fills missing units.
`revenue` fills units and appends revenue_cents. `group` and `monthly` normalize
regions, fill units and derive revenue, then aggregate by region or month/region.
`lookup` normalizes region, derives revenue and appends revenue_cents_per_target;
unknown/zero/missing targets produce None. `window` derives revenue and appends a
trailing-row mean (window sizes 2, 3, or 4), excluding missing revenue values.

Fill policy is `request['fill']` (`zero`, `mean`, or `median`); all-missing input
fills with zero. Aggregation is `request['agg']` (`sum`, `mean`, or `count`), with
mean of an empty set represented by None. Aggregation count counts nonmissing
revenue. Group outputs omit missing grouping keys and sort keys lexically by
string form. Original row columns remain in their original order; derived fields
are appended. Invalid policy values and invalid window sizes raise ValueError.
