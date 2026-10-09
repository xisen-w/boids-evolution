# table transforms

Import the family adapters directly: `from candidate import clean, revenue, group, monthly, lookup, window`. Each has signature `(rows, lookup, request)`; rows and lookup are lists of dictionaries, and inputs are never mutated. `request` must supply `fill` (`zero`, `mean`, or `median`) for all families; grouped families also require `agg` (`sum`, `mean`, `count`), and window requires `window` (2, 3, or 4).

Example:
```python
from candidate import revenue
rows = [{'region':' West ', 'units':2, 'price_cents':125}]
assert revenue(rows, [], {'fill':'mean'})[0]['revenue_cents'] == 250
```

Region strings are stripped and lowercased. Missing units are imputed from present units (all missing becomes zero); revenue is `units * price_cents`, or `None` if price is missing. Group/monthly omit missing keys and ignore missing revenue for aggregation. Lookup uses exact keys after row region normalization; unknown, missing, or zero targets produce `None`. Window means over trailing rows including the current row, skipping missing revenues.

Limitations: expected input types follow the publication contract (numeric operands, string dates/regions); invalid fill/aggregate/window values raise `ValueError`. No external dependencies.
