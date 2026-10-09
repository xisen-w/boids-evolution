# Row-table services

Pure Python service adapters, imported as `from candidate import clean, revenue, group, monthly, lookup, window`. Each function accepts `(rows, lookup, request)` and returns new dicts without mutating the inputs. The package delegates to `published.a04_r04`.

Example: `monthly([{'region':' West ', 'date':'2025-03-12', 'units':2, 'price_cents':50}], [], {'fill':'mean', 'agg':'sum'})` returns `[{'month':'2025-03', 'region':'west', 'sum_revenue_cents':100}]`.

`clean` normalizes region and fills missing units; `revenue` derives `revenue_cents`; `group` and `monthly` aggregate nonmissing revenue with sum/mean/count; `lookup` adds per-target revenue; `window` computes trailing-row revenue mean. Fill modes are zero/mean/median (all-missing units fill with zero); aggregate modes are sum/mean/count. Row-preserving services retain columns/order. Group services omit missing group keys. Inputs are expected to follow the documented service schema and valid parameter values.
