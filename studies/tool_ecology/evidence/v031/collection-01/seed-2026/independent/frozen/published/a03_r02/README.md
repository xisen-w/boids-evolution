# Native tabular transformations

Dependency-free Python functions accept `(rows, lookup, request)` and return new lists of dictionaries without mutating inputs. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

`clean` normalizes string region values (strip/lower) and fills missing units. `revenue` fills units and appends `revenue_cents` (missing operands give None), without normalizing region. `group` normalizes regions and returns grouped revenue; `monthly` additionally groups by date's YYYY-MM prefix. Both drop missing group keys and accept `request['agg']` = sum/mean/count. `lookup` normalizes region and appends revenue divided by exact-region lookup target; unavailable, zero, or missing targets yield None. `window` appends the mean of nonmissing revenue among the current row and preceding `window-1` rows.

All functions require `request['fill']` in zero/mean/median; aggregate functions require `agg` in sum/mean/count; window requires window 2, 3, or 4. Missing-unit mean/median on empty data resolve to zero. Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns a row with `revenue_cents: 100`.
