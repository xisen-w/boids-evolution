# Tabular service dispatcher

This package provides a named dispatcher around the verified native adapters in `published.a07_r02` rather than duplicating their transformation logic.

## API

`process(family, rows, lookup_rows, request)` accepts one of `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window`; it returns that family's complete output and raises `ValueError` for an unknown family. For example:

```python
from candidate import process
result = process('revenue', [
    {'region': 'West', 'units': 2, 'price_cents': 75}
], [], {'fill': 'zero'})
# [{'region': 'West', 'units': 2, 'price_cents': 75, 'revenue_cents': 150}]
```

The six root adapter functions (`clean_adapter`, `revenue_adapter`, `group_adapter`, `monthly_adapter`, `lookup_adapter`, `window_adapter`) have the same `(rows, lookup, request)` signature and correspond directly to those services. Input semantics, options, ordering and limitations are those documented by `published.a07_r02`; requests are not modified.
