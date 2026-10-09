# Table services

All APIs accept `rows, lookup, request` and return new lists/dictionaries without mutating inputs. `clean(rows, lookup, request)` normalizes string regions via strip/lower and fills missing units using `request['fill']` (`zero`, `mean`, or `median`; default `zero`; all-missing becomes zero), preserving columns and order. `revenue` does the same and appends `revenue_cents`, null when units or price is null.

`group` and `monthly` additionally require `request['agg']` (`sum`, `mean`, `count`; default `sum`). Group drops missing keys and emits sorted groups. Monthly groups by date prefix `YYYY-MM` and region, dropping either missing key. Both return their keys and `<agg>_revenue_cents`; mean of an empty set is null, sum/count are zero.

`lookup` appends `revenue_cents_per_target`, using normalized region-key matching against lookup rows; missing/zero target or revenue gives null. It does not add lookup columns. `window` appends the trailing-row mean `roll_revenue_cents`; `request['window']` must be 2, 3, or 4. Null revenues are ignored within the fixed row window.

Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a copied row with region `west` and revenue 100. Unknown fill/aggregation and unsupported windows raise `ValueError`.
