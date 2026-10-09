# Native table services

Dependency-free Python adapters for six table transformations. Import with `from candidate import clean, revenue, group, monthly, lookup, window`; each takes `(rows, lookup, request)` and returns fresh output without mutating inputs.

`clean` normalizes region and fills missing units (`zero`, `mean`, `median`; all missing -> 0). `revenue` fills units and appends `revenue_cents`. `group` and `monthly` aggregate nonmissing revenue by normalized region or `(date[:7], region)`, dropping missing keys; `request['agg']` is `sum`, `mean`, or `count`. `lookup` normalizes region and appends `revenue_cents_per_target` from normalized exact region lookup; unknown keys, zero/missing targets and missing revenue yield `None`. `window` adds trailing-row mean `roll_revenue_cents` over `request['window']` rows including current.

Example: `revenue([{'units': 2, 'price_cents': 5}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 5, 'revenue_cents': 10}]`. Grouped output is sorted by stringified key(s); other row services preserve input order and fields.
