# tabular services

Dependency-free Python functions accepting `(rows, lookup, request)`. Each returns new dicts and does not mutate inputs. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.

`clean` normalizes non-null regions with strip/lower and fills null units. `revenue` fills units and adds `revenue_cents`. `group` and `monthly` normalize/fill/derive, then aggregate non-null revenue; monthly derives the first seven date characters. `lookup` adds the per-target quotient without adding lookup columns. `window` adds the trailing ROWS mean including current row. Fill accepts `zero`, `mean`, `median` (default zero); all-null units fill to zero. Aggregate accepts `sum`, `mean`, `count` (default sum). Window size is 2, 3, or 4.

Example: `revenue([{'units': None, 'price_cents': 5}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 5, 'revenue_cents': 0}]`.

Limitations: rows are expected to be dictionaries with the service schema; month extraction assumes ISO date strings. Unknown fill/aggregate/window values raise `ValueError`.
