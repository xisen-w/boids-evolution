# Tabular service adapters

Dependency-free Python functions accepting `(rows, lookup, request)`; inputs are not mutated. Each returns a new list of row dictionaries or aggregate dictionaries. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup_service`, and `window`.

`clean` fills missing units (`fill`: zero/mean/median; all missing becomes zero) and strips/lowercases region. `revenue` fills units and appends `revenue_cents` (None if units or price is None) without changing other columns. `group` and `monthly` normalize region, derive revenue, and aggregate nonmissing revenue using `agg` sum/mean/count; monthly keys derive from the first seven date characters. Both omit missing grouping keys. `lookup_service` normalizes and derives revenue, then appends ratio from exact normalized region lookup; absent/None/zero targets produce None. It does not add lookup fields. `window` derives revenue and appends trailing row-window mean, default window 2; supported values are 2, 3, 4.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.
