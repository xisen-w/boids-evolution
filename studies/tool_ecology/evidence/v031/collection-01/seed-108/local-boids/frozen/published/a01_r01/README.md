# tabular_services

Pure-Python adapters for six row-table services. Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` each take a list of row dictionaries, a lookup-row list, and a request dictionary and return a new list without mutating inputs. Missing fill defaults to `zero`; supported values are `zero`, `mean`, and `median`. Aggregation defaults to `sum`; supported values are `sum`, `mean`, and `count`. Window defaults to 2 and uses trailing rows including the current row.

Example:
```python
from candidate import revenue
rows = [{'region':' West ', 'units':None, 'price_cents':25}]
assert revenue(rows, [], {'fill':'zero'})[0]['revenue_cents'] == 0
```

Clean preserves all other columns and row order. Revenue-derived services add `revenue_cents` (None when price is missing). Group and monthly omit missing group keys; monthly uses the first seven date characters. Lookup adds only `revenue_cents_per_target` beyond the normalized/revenue columns; lookup keys are stripped and lowercased. Window adds the mean of available revenues in the specified trailing ROWS interval. Inputs are expected to contain standard service fields; malformed dates are not validated. All-missing units fill with zero.
