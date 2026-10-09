# Table service adapters

Native Python package with six root-level functions. Each function has the signature `family(rows, lookup, request)` and returns fresh dictionaries without mutating its inputs. The input tables are lists of dictionaries; requests support `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (row count).

```python
from candidate import clean, revenue, group, monthly, lookup as lookup_service, window
rows = [{'id': 1, 'region': ' EAST ', 'product': 'x', 'date': '2025-01-02', 'units': 2, 'price_cents': 50}]
cleaned = clean(rows, [], {'fill': 'zero'})
assert cleaned[0]['region'] == 'east'
assert revenue(rows, [], {})[0]['revenue_cents'] == 100
assert group(rows, [], {'agg': 'sum'}) == [{'region': 'east', 'sum_revenue_cents': 100}]
```

Clean normalizes non-null region values and fills missing units across the input table (all missing becomes zero), preserving columns and row order. Revenue derives `revenue_cents` without normalizing region. Group and monthly normalize regions and omit missing group keys; missing revenue is ignored, with empty sum/count equal to zero and empty mean `None`. Lookup normalizes regions and appends a per-target ratio (`None` for missing revenue, missing/zero target, or unmatched region); lookup metadata is not appended. Window keeps row order and computes a mean over nonmissing revenues within each trailing row window, including the current row. Derived keys are appended to each row. Inputs are expected to use the documented service schema and valid request parameter values.
