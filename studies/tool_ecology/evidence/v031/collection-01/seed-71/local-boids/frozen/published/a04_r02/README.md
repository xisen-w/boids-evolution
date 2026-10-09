# Row services

Native Python functions accept `rows, lookup, request` and return new dictionaries/lists without mutating inputs. Public adapters: `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`.

`clean` normalizes string regions by strip/lower and fills missing units. `revenue` fills units and appends `revenue_cents` but preserves the region as supplied. `group` and `monthly` normalize regions, derive revenue, and aggregate using `request['agg']` (`sum`, `mean`, `count`); monthly groups by date prefix `YYYY-MM`. `lookup` normalizes regions, appends revenue divided by the matching region target (None for missing/zero target or revenue). `window` appends the mean of nonmissing revenues over trailing rows, including current; width is `request['window']`.

All services use `request['fill']` (`zero`, `mean`, `median`) when imputing; all-missing units become zero. Example:

```python
from candidate import revenue
rows = [{'region': ' North ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'region': ' North ', 'units': 2, 'price_cents': 50, 'revenue_cents': 100}]
```

Group output columns are `<agg>_revenue_cents`; missing grouping keys are dropped. Limitations: expects dictionaries with the documented service input fields and valid request choices; dates are grouped by their first seven characters.
