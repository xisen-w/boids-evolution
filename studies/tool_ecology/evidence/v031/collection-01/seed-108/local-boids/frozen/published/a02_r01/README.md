# Table services

Native Python, no external dependencies. Each public adapter has signature
`service(rows, lookup, request)`; it returns new dictionaries and does not mutate inputs.

* `clean(rows, lookup, request)`: lowercases/strips string regions and fills missing
  units (`fill`: `zero`, `mean`, or `median`; default `zero`, all missing -> 0).
* `revenue(...)`: clean behavior plus `revenue_cents` (None if units or price is None).
* `group(...)`: revenue behavior grouped by region; `agg` is `sum`, `mean`, or `count`
  (default `sum`); missing keys are excluded and count counts nonmissing revenues.
* `monthly(...)`: same aggregation by `(date[:7], region)`; missing keys excluded.
* `lookup(...)`: adds `revenue_cents_per_target`; lookup region strings are normalized
  like row regions. Missing/zero targets or missing revenue produce None.
* `window(...)`: adds `roll_revenue_cents`, the mean of nonmissing revenue values in
  the trailing `window` rows including current (`2`, `3`, or `4`; default 2).

Example: `from candidate import group; group(rows, [], {'fill':'zero','agg':'sum'})`.
All adapters retain input column order and append derived fields; aggregate output is
sorted lexicographically by stringified grouping keys. Dates are expected as ISO strings.
Unknown fill/aggregation/window values raise ValueError. Lookup duplicate normalized
regions use the last supplied target. Numeric values are used as supplied.
