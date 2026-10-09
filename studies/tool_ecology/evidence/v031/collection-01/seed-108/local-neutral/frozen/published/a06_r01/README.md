# Table service transformations

Native Python, no third-party dependencies. Public functions accept `(rows, lookup, request)` and return new dictionaries without mutating inputs. `clean`, `revenue`, `group`, `monthly`, `lookup_revenue`, and `window` implement the corresponding service families. All normalize string regions with strip/lower; fill accepts `zero`, `mean`, or `median` (all missing becomes zero). Aggregation accepts `sum`, `mean`, or `count`; rolling window honors request `window` (2/3/4).

Example:
```python
from candidate import revenue
rows = [{'region':' West ', 'units':2, 'price_cents':50}]
assert revenue(rows, [], {'fill':'zero'}) == [
 {'region':'west', 'units':2, 'price_cents':50, 'revenue_cents':100}]
```

Missing revenue operands yield `None`; grouped outputs drop missing keys, and lookup target matching is exact after region normalization. APIs expect iterable lists of dictionaries with the service schema; malformed requests/rows are not validated. Group sum/count on groups containing only missing revenue produce zero; mean produces None.
