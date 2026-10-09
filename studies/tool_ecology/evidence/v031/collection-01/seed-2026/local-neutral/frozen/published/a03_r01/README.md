# Candidate table services

All public functions are at package root and have signature `function(rows, lookup, request)`. They return new list/dict objects and do not mutate inputs. Rows are dictionaries; region strings are stripped and lowercased. Missing numeric values are `None`.

* `clean(rows, lookup, request)`: copies rows, normalizes region and fills missing units using request `fill` (`zero`, `mean`, or `median`; all missing becomes zero). Example: `clean(rows, [], {'fill':'median'})`.
* `revenue(...)`: same fill behavior, plus `revenue_cents`, null if units or price is null.
* `group(...)`: normalized region/revenue, then output records with `region` and `<agg>_revenue_cents`; `agg` is sum, mean, or count. Missing region groups are dropped; count counts non-null revenues.
* `monthly(...)`: same revenue derivation, grouped by nonmissing month (`date[:7]`) and region, sorted by keys.
* `lookup(...)`: adds `revenue_cents_per_target` from lookup region/target, normalizing lookup region for matching; unknown, null/zero target, or null revenue yields null. Does not add lookup fields.
* `window(...)`: adds trailing-row mean `roll_revenue_cents`, including current row, with width 2, 3, or 4 from request.

Aggregation of empty values is zero for sum/count and null for mean. Outputs preserve input order except group outputs, which are sorted. Lookup uses the last target if duplicate normalized lookup regions occur. Inputs are expected to use the documented request options and row schema; no validation is promised for malformed dates or nonnumeric values.
