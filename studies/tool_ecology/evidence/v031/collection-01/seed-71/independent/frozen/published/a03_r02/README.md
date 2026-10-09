# Native row-table transforms

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from this package. Each callable accepts `(rows, lookup, request)` and returns newly allocated dictionaries; inputs are not mutated.

- `clean`: normalize region with strip/lower and fill missing units.
- `revenue`: fill units and append `revenue_cents`; region remains unchanged.
- `group`: normalized-region revenue aggregate; request `agg` is `sum`, `mean`, or `count`.
- `monthly`: normalized region/month revenue aggregate with the same `agg` choices.
- `lookup`: normalized-region revenue per target from exact normalized region lookup.
- `window`: revenue and trailing-row rolling mean; request `window` must be 2, 3, or 4.

All functions take request `fill` as `zero`, `mean`, or `median`. Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'region': None, 'revenue_cents': 100}]`. Revenue preserves existing keys without region normalization.
