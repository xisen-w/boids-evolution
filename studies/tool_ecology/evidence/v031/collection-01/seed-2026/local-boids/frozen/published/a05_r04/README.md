# Tabular service adapters

Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. All accept lists of dictionaries and return new dictionaries/lists without mutating inputs.

Row adapters preserve input columns/order. `clean` normalizes string regions with strip/lower and fills missing units. `revenue` additionally appends `revenue_cents`. Fill mode is `request['fill']`: zero, mean, or median (default zero); all-missing is zero and even median averages middle values. Missing operands produce None revenue.

`group` outputs region plus `<agg>_revenue_cents`; `monthly` outputs month, region, and that aggregate. They omit missing keys, ignore missing revenue, sort keys lexically, and support sum/mean/count (`request['agg']`, default sum). Empty aggregate values are 0 for sum/count and None for mean. `window` adds mean of nonmissing revenue within trailing ROWS including current; width is `request['window']` (2/3/4, default 2).

`lookup` normalizes row and lookup region strings for exact matching and appends `revenue_cents_per_target`; unknown/missing/zero target or missing revenue yields None. It does not add target or manager.

Example: `revenue([{'region':' West ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns a row with original values and `revenue_cents: 100`.

Implementation reuses verified native adapters from `published.a04_r02`; inputs are expected to follow the documented schema.
