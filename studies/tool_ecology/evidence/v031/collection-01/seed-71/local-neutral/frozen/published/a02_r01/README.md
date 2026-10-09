# Tabular service helpers

Import with `from candidate import clean, revenue, group, monthly, lookup, window`.
Every function has signature `(rows, lookup, request)` and returns new dictionaries without mutating inputs. Rows retain their input column order (new fields are appended); group outputs have only their documented aggregate columns. Region strings are stripped and lowercased; missing regions stay `None`.

* `clean(rows, lookup, request)`: fills missing `units` using `request['fill']` (`zero`, `mean`, or `median`; default zero), retaining all row fields.
* `revenue(...)`: applies the same fill and appends `revenue_cents` (`units * price_cents`, or `None` when price is missing).
* `group(...)`: additionally groups by normalized region, drops missing region keys, and aggregates nonmissing revenue using `request['agg']` (`sum`, `mean`, `count`; default sum). Example: `group(rows, [], {'fill':'zero','agg':'mean'})` returns rows with `region` and `mean_revenue_cents`.
* `monthly(...)`: groups by `date[:7]` and normalized region, dropping missing keys; for example `monthly(rows, [], {'agg':'sum'})` emits `month`, `region`, `sum_revenue_cents`.
* `lookup(...)`: appends `revenue_cents_per_target`; lookup keys are normalized like row regions, and missing/zero targets or missing revenue yield `None`. Example: `lookup(rows, [{'region':'west','target':2}], {'fill':'zero'})`.
* `window(...)`: appends trailing row-window mean `roll_revenue_cents`; `request['window']` must be 2, 3, or 4 (default 2). Example: `window(rows, [], {'window':3})`.

Group/monthly support empty groups: sum and count are zero, mean is `None`. Unknown fill/aggregation values raise `ValueError`. Input rows are expected to be dictionaries with the service schema; dates are expected to be ISO strings when present.
