# Candidate table services

Public APIs: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_revenue(rows, lookup, request)`, and `window(rows, lookup, request)`. Equivalent service adapters are `clean_service`, `revenue_service`, `group_service`, `monthly_service`, `lookup_service`, and `window_service`; each takes three arguments.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

Missing values use None. Fill accepts zero/mean/median (default zero), aggregation sum/mean/count (default sum), and window accepts 2/3/4 (default 2). Inputs are not mutated. Revenue/window retain the input region unchanged; clean/group/monthly/lookup normalize strings by stripping and lowercasing. Lookup compares normalized region keys. Invalid fill/aggregation/window values raise ValueError. Dates are expected to be strings supporting `[:7]`.
