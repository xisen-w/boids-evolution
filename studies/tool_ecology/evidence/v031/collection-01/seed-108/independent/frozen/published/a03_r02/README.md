# Table services

Pure Python adapters accept `(rows, lookup, request)` using list-of-dict inputs and return new data without mutating inputs. Import the six root functions: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

`clean` normalizes region by strip/lower and fills missing units; `revenue` fills units and appends `revenue_cents` but preserves region as supplied. Fill is `zero`, `mean`, or `median`; all-missing units become zero. Revenue is null if either operand is null. Group and monthly normalize region and return grouped aggregates (`request.agg` is sum/mean/count), dropping null grouping keys; monthly groups on the first seven date characters. Lookup normalizes regions for exact matching and appends revenue per target; missing/zero target or missing revenue gives null. Window appends the mean of nonnull revenue in the trailing `request.window` rows including current, or null if empty (window is 2, 3, or 4).

Group and monthly output only keys and aggregate field, sorted lexically by stringified keys. Count excludes missing revenues. Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` gives `{'units': 2, 'price_cents': 50, 'revenue_cents': 100}`.

Inputs are expected to follow the documented schema and valid options; malformed values are not specially handled.
