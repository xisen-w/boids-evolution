# Tabular service transforms

Native Python functions accept `(rows, lookup, request)` and return fresh row dictionaries (or grouped output); inputs are not mutated. Public adapters: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

- `clean`: normalize nonmissing regions using strip/lower and fill units (`fill`: zero/mean/median; default zero).
- `revenue`: fill units and derive `revenue_cents`; region is left unchanged.
- `group` / `monthly`: normalized regions, revenue derivation, then nonmissing-key aggregation (`agg`: sum/mean/count; default sum).
- `lookup`: normalized region/revenue and `revenue_cents_per_target` based on region-keyed lookup.
- `window`: revenue and trailing ROWS mean (`window`: 2, 3, or 4; default 2); original region is unchanged.

Example: `revenue([{'units': 2, 'price_cents': 10, 'region': ' X '}], [], {'fill':'zero'})` returns a copied row with `revenue_cents: 20` and unchanged region. Empty means are `None`; sum/count of empty nonmissing values are zero. This module expects mapping-like rows and standard string regions.
