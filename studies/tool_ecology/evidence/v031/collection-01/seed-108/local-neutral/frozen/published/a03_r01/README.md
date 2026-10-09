# rowservices

Pure-Python row-table services. Public functions accept `(rows, lookup=None, request=None)` and return new dictionaries; inputs are not modified. `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` implement the corresponding service families. Request keys are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (2, 3, or 4); defaults are zero, sum, and 2. Missing units are filled over the whole input. All-missing units fill to zero. Revenue is `units * price_cents`, or `None` if either operand is missing.

Example:

```python
from candidate import revenue
rows = [{'units': 2, 'price_cents': 125}]
assert revenue(rows)[0]['revenue_cents'] == 250
```

Grouping omits missing keys and ignores missing revenue in aggregates; empty-value sums/counts are zero and means are None. Region normalization strips and lowercases. Lookup uses normalized row regions as exact keys against the supplied lookup table's region values; missing/zero targets yield None. Services preserve original row columns/order and append derived columns, except group/monthly which return aggregate rows. Unsupported request values raise ValueError. Values are expected to be numeric where arithmetic applies and dates to be ISO-formatted strings.
