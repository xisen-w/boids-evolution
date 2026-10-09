# a02_r06 tabular services

Dependency-free Python adapters for six row-table services. Public API functions are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`. Each returns fresh dicts/lists and does not mutate inputs. Requests use `fill` (`zero`, `mean`, `median`; default `zero`), and grouped APIs use `agg` (`sum`, `mean`, `count`; default `sum`). Window uses `window` 2, 3, or 4 (default 2).

Example: `from candidate import revenue; revenue([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero'})` yields a normalized row with `revenue_cents: 100`.

`clean` normalizes region and fills units; `revenue` normalizes region and derives revenue; `group`/`monthly` return aggregates, excluding missing group keys; `lookup_service` adds revenue divided by exact normalized-region target; `window` computes a trailing row-window mean. Missing operands yield null revenue. Lookup targets are expected to use the same normalized region keys. Inputs are lists of dictionaries with numeric values or `None`; unsupported fill/agg/window options raise `ValueError`.
