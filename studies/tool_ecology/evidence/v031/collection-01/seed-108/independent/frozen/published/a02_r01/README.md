# tabular_services

Native-Python adapters implementing the six recurring row-table services. Import with `from candidate import clean, revenue, group, monthly, lookup, window`; each function takes `(rows, lookup, request)` and returns new dictionaries without mutating inputs. Missing optional request parameters default to `fill='zero'` and `agg='sum'`; window requires 2, 3, or 4. Fill accepts `zero`, `mean`, or `median` (all-missing units fill with zero); aggregation accepts `sum`, `mean`, or `count`.

Example: `revenue([{'region':' West ','units':2,'price_cents':150}], [], {'fill':'zero'})` returns the row with normalized region `west` and `revenue_cents=300` (unmentioned source fields are preserved). `group(rows, [], {'fill':'zero','agg':'sum'})` returns sorted region groups. `monthly` groups by date prefix and region; `lookup` adds revenue per normalized lookup region's target; `window` computes the trailing-rows mean.

Limitations: rows are expected to be mappings and date values, when present, strings in ISO format. No validation is performed for numeric field types; invalid fill/aggregation/window values raise `ValueError`. Lookup region strings are normalized using the same strip/lower rule.
