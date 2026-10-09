# Row revenue helpers

Native Python, nonmutating implementations of the `revenue` and `window` service adapters.

* `revenue(rows, lookup, request)` fills missing `units` according to `request['fill']` (`zero`, `mean`, or `median`; default `zero`; all-missing becomes zero), then adds/replaces `revenue_cents`. It preserves row order and other keys, and does not normalize region. A missing price produces `None` revenue.
* `window(rows, lookup, request)` returns the revenue result plus `roll_revenue_cents`, the mean of nonmissing revenues within the trailing `request['window']` row positions including the current row (default 2). Empty windows yield `None`.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`.

Both APIs accept `(rows, lookup, request)`; lookup is unused. Input rows are copied. Invalid fill modes or nonpositive/noninteger window widths raise `ValueError`.
