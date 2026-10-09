# rowservices

Native Python row-oriented service adapters. Public APIs are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup, request)`, and `window(rows, lookup, request)` (also exported as top-level functions). Inputs are lists of dictionaries; functions return new dictionaries and do not mutate inputs. `lookup` is an argument name and function name; lookup rows use exact region keys.

`request.fill` is `zero`, `mean`, or `median` (default `zero`); missing units are filled before revenue derivation, with all-missing inputs filled as zero. `request.agg` for group/monthly is `sum`, `mean`, or `count` (default `sum`); mean on an empty set is `None`. Group and monthly omit missing group keys. `request.window` is 2, 3, or 4 (required for window); rolling means cover trailing rows including current and ignore missing revenue values. Region strings are stripped and lowercased for clean/group/monthly/lookup.

Example: `group([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero','agg':'sum'})` returns `[{'region':'west','sum_revenue_cents':100}]`.

Derived columns are appended in revenue services. The adapters target the documented input schema; malformed numeric values and malformed dates are not specially validated. `lookup` uses exact matching after input region normalization and does not add target or manager columns.
