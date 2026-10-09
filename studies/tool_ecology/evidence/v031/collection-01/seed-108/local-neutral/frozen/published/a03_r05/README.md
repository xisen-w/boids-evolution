# Row-table services

Native Python adapters expose `function(rows, lookup, request)` and return new lists of dictionaries without mutating inputs. The implementation delegates to the previously service-verified `a03_r04` package (transitively dependent on `a03_r03`).

Exports: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window` and corresponding `_service` names. Example:

```python
from candidate import revenue
result = revenue([{'region':' West ', 'units':2, 'price_cents':125}], [], {'fill':'zero'})
assert result[0]['region'] == 'west'
assert result[0]['revenue_cents'] == 250
```

`fill` is `zero`, `mean`, or `median` (default `zero`); `agg` is `sum`, `mean`, or `count` (default `sum`); `window` is 2, 3, or 4 (default 2). Clean fills units and normalizes region. Revenue derives cents; group/monthly aggregate nonmissing revenues; lookup adds revenue per exact normalized region target; window calculates trailing-row mean. Grouped output drops missing keys. Inputs should use the specified dictionary schema and valid options.
