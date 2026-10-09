# tabular_services

Pure-Python adapters for the six row-table service families. Public functions are
`clean(rows, lookup, request)`, `revenue(rows, lookup, request)`,
`group(rows, lookup, request)`, `monthly(rows, lookup, request)`,
`lookup(rows, lookup_rows, request)`, and `window(rows, lookup_rows, request)`.
All return fresh dictionaries and do not mutate inputs. Requests use `fill`
(`zero`, `mean`, or `median`; default `zero`), `agg` (`sum`, `mean`, or
`count`; default `sum`), and `window` (2, 3, or 4) as applicable.

Example: `group(rows, [], {'fill':'mean', 'agg':'sum'})` normalizes region,
fills missing units, computes row revenue and returns sorted region totals.
`clean` returns normalized/fill-adjusted input columns only. `revenue`,
`lookup`, and `window` append their named derived columns. Group results omit
null region keys; monthly results omit null month or region keys. Lookup keys
are exact and are not normalized; unknown/null/zero targets produce null
ratios. Date month is the first seven characters of the supplied ISO date.
Only `None` is treated as missing. Invalid request choices raise `ValueError`.
