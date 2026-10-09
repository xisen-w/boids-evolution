# Tabular transformations

This package exposes six native Python service adapters, reusing the DEV-verified
implementation in `published.a02_r02` rather than duplicating its algorithms.

Every function accepts `(rows, lookup, request)` and returns a fresh list of
row dictionaries. `clean` normalizes region and fills missing units;
`revenue` fills units and derives `revenue_cents`; `group` and `monthly`
normalize regions, derive revenue and aggregate; `lookup` adds
`revenue_cents_per_target`; `window` adds the trailing ROWS revenue mean.
Request options are `fill` (`zero`, `mean`, `median`), `agg` (`sum`, `mean`,
`count`), and `window` (2, 3, or 4), as applicable. See the dependency's
README for detailed semantics.

Example:

```python
from candidate import revenue
rows = [{'region': 'North', 'units': 2, 'price_cents': 50}]
result = revenue(rows, [], {'fill': 'zero'})
assert result[0]['revenue_cents'] == 100
```

Inputs are not mutated. This package requires `published.a02_r02`; it does not
provide independent behavior beyond that implementation. Input rows must be
mapping-like, with standard string regions where present.
