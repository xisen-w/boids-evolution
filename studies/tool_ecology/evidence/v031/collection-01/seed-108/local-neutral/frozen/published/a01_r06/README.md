# Row services

Six root callables accept `(rows, lookup, request)` and return fresh dictionaries: `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service`. Example: `revenue_service([{"region":" N ","units":2,"price_cents":50}], [], {"fill":"mean"})` returns a row with normalized region `n` and revenue 100.

Fill is zero/mean/median (all-missing units fill to 0; even median averages middle values). Aggregations are sum/mean/count; grouped null keys are dropped and count excludes missing revenue. Monthly keys use date[:7]. Lookup adds only per-target revenue. Window means nonmissing values among the trailing window rows including current. Inputs are not mutated. Inputs are expected to follow the specified mapping schema and valid request parameter choices.
