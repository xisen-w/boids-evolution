# Row table transforms

Native Python, no dependencies. Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` accept lists of dictionaries and a request dictionary; they return new dictionaries without mutating inputs.

`clean` normalizes region strings and fills null units (`fill`: zero/mean/median, default zero). `revenue` fills units and appends revenue cents, without changing region values. `group` and `monthly` normalize region and aggregate nonmissing revenue (agg sum/mean/count, default sum); results omit null group keys and sort stringified keys. `lookup` normalizes region and appends revenue per exact-region target, null for absent/zero target or absent revenue. `window` appends the trailing ROWS mean (request window 2/3/4) of nonmissing revenue. All preserve original fields/order in row-oriented outputs; aggregates contain only result fields.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`. Empty mean groups yield None; sum/count yield zero. Missing numeric units fill to zero when all missing.
