# Row analytics

Native Python package with six service adapters. Every adapter has signature
`family(rows, lookup, request)` and returns fresh dictionaries without mutating inputs.

- `clean(rows, lookup, request)`: normalizes nonmissing regions with strip/lower and fills missing units using `request['fill']` (`zero`, `mean`, `median`; default zero).
- `revenue(...)`: same preparation plus `revenue_cents` (None if either operand is None).
- `group(...)`: group by normalized region and aggregate nonmissing revenue using `request['agg']` (`sum`, `mean`, `count`; default sum).
- `monthly(...)`: group by month (first seven date characters) and region.
- `lookup(...)`: appends revenue divided by target from normalized exact region lookup. Unknown, missing, or zero targets yield None.
- `window(...)`: appends mean revenue over trailing physical rows including current; `request['window']` is 2, 3, or 4 (default 2).

Grouped results omit missing keys and sort lexicographically by stringified keys. Empty group aggregates do not occur; empty sums/counts are naturally zero. Count counts nonmissing revenue. Group output uses `<agg>_revenue_cents`. Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a row with region `west` and revenue 100.

Inputs are expected to be lists of dictionaries with the documented service fields. Invalid fill/aggregate/window values raise ValueError. Missing region/date keys are supported as None; date values are expected to be strings.
