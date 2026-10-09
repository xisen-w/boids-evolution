# Row services

This package exposes six adapters with signature `(rows, lookup, request)`:

* `clean`: normalize string regions with strip/lower and fill missing units.
* `revenue`: fill missing units and append `revenue_cents`.
* `group`: normalize regions and aggregate revenue by region.
* `monthly`: normalize regions and aggregate revenue by month and region.
* `lookup`: normalize regions and add revenue per region target.
* `window`: add trailing-row mean revenue (including the current row).

Fill mode is `request['fill']` (`zero`, `mean`, or `median`; defaults to
`zero`). Aggregation is `request['agg']` (`sum`, `mean`, or `count`; defaults
to `sum`). Window width is `request['window']` (defaults to 2). Missing units
are imputed across the input; all-missing units fill with zero. Missing revenue
is excluded from aggregates and window means. Group outputs omit missing keys;
mean of an empty aggregate is `None`, while sum/count are zero. Lookup results
are `None` for unknown regions, missing/zero targets, or missing revenue.
Original columns and order are retained on row outputs. `lookup` means the
lookup-record table argument, not the function's data rows.

Example:

```python
from candidate import revenue, group
rows = [{'region': ' N ', 'units': 2, 'price_cents': 50}]
assert revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents'] == 100
assert group(rows, [], {'fill': 'zero', 'agg': 'sum'}) == [
    {'region': 'n', 'sum_revenue_cents': 100}]
```

The public adapters are thin re-exports of the tested `published.a04_r02`
implementation; invalid modes follow that dependency's `ValueError` behavior.
