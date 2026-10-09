# Tabular row services (compatibility publication)

This package exposes the six pure-Python row service adapters from the verified
`a04_r04` implementation. Import with `from candidate import clean, revenue,
group, monthly, lookup, window`. Each function takes `(rows, lookup, request)`
and returns a fresh list of dictionaries; inputs are not modified.

- `clean`: normalize region strings and fill missing units.
- `revenue`: fill units and add `revenue_cents`.
- `group`: aggregate revenue by normalized region.
- `monthly`: aggregate by month and normalized region.
- `lookup`: add revenue per exact region-key target.
- `window`: add trailing-row rolling revenue mean.

Request options are `fill` (`zero`, `mean`, or `median`; default `zero`),
`agg` (`sum`, `mean`, or `count`; default `sum`), and `window` (2, 3, or 4
for the window adapter). Median averages the central pair when needed;
all-missing units fill with zero. Grouping omits missing keys and count excludes
missing revenues. Lookup results are `None` for unknown regions, absent/zero
targets, or missing revenue. Rolling means consider the trailing number of
rows, including current, and ignore missing revenue values. Inputs are expected
to use the documented row schema and types.

Example:
```python
from candidate import clean, revenue
rows = [{'region': ' NORTH ', 'units': None, 'price_cents': 20}]
req = {'fill': 'zero'}
assert clean(rows, [], req)[0]['region'] == 'north'
assert revenue(rows, [], req)[0]['revenue_cents'] == 0
```
