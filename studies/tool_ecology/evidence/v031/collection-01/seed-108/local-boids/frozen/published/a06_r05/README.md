# Row-table service adapters

Dependency-light public entry points for the six row-table service families. The implementations are reused from `published.a06_r02` rather than reimplemented here.

## API

Each callable accepts `(rows, lookup, request)` and returns newly constructed output without mutating its arguments:

* `clean`: normalize region by stripping/lowercasing and fill missing units.
* `revenue`: fill units and append `revenue_cents` (None when a product operand is missing); original region is retained.
* `group`: normalized regions and revenue, grouped by region with selected aggregate.
* `monthly`: normalized regions and revenue, grouped by month and region.
* `lookup`: normalized regions and revenue, then append revenue per matching region target.
* `window`: revenue plus a trailing-row mean in `roll_revenue_cents`.

Fill services use `request['fill']` (`zero`, `mean`, or `median`; defaults to zero). Aggregations use `request['agg']` (`sum`, `mean`, or `count`; defaults to sum). Window width is `request['window']` (defaults to 2). Aggregates ignore missing revenue; empty sum/count are zero and empty mean is None. Output schemas, sorting, and missing-value behavior follow the recurring service specifications.

Example:

```python
from candidate import revenue
rows = [{'region': ' East ', 'units': None, 'price_cents': 5}]
assert revenue(rows, [], {'fill': 'zero'}) == [
    {'region': ' East ', 'units': 0, 'price_cents': 5, 'revenue_cents': 0}
]
```

Inputs are expected to be lists of dictionaries with the service schema and valid option values. No external third-party dependencies are required.
