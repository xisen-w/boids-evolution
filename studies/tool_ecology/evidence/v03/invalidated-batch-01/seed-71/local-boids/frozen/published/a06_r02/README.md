# Row-service facade

Dependency-light public facade reusing the tested `published.a00_r01` implementation. Each function accepts `(rows, lookup, request)` and returns the corresponding family output:

- `clean`: fill missing units (`request.fill`: zero/mean/median) and normalize regions.
- `revenue`: fill units and append `revenue_cents`.
- `group`: normalized region aggregation (`request.agg`: sum/mean/count).
- `monthly`: month-and-region aggregation with the same aggregate choices.
- `lookup`: append per-target revenue using exact lookup-region keys.
- `window`: append trailing-row revenue mean; `request.window` is 2, 3, or 4.

Example: `group([{'region':' West ', 'units':2, 'price_cents':50}], [], {'fill':'zero','agg':'sum'})` returns `[{'region':'west','sum_revenue_cents':100}]`.

Functions return fresh row dictionaries and preserve source row order where applicable. Aggregations omit missing grouping keys; means of empty aggregates are `None`. Lookup adds no lookup metadata columns. The facade follows the dependency's schema and validation behavior; it does not independently validate malformed data.
