# Tabular services

Dependency-free native Python adapters for the six specified row-table services.
Public functions `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)` return fresh dictionaries/lists and do not mutate inputs. `lookup` is the list of region/target/manager records; unused for other families. Request accepts `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`, `count`), and `window` (row width). Missing unit values are filled (all-missing becomes zero; median averages central values). Revenue and window preserve original region strings; group/monthly/lookup normalize region with strip/lower. Derived columns are appended. Group outputs omit null keys and sort stringified keys; monthly groups by YYYY-MM and normalized region. Lookup emits `revenue_cents_per_target`, null for absent/zero targets or missing revenue. Window averages nonmissing revenue in trailing rows including current.

Example: `revenue([{'units': None, 'price_cents': 10}], [], {'fill':'zero'})` returns `[{'units': 0, 'price_cents': 10, 'revenue_cents': 0}]`.

Inputs are assumed to follow the documented service schemas and valid request choices.
