# Tabular services

Pure-Python implementations of the six row-table service families. Public functions are `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`, `monthly(...)`, `lookup(...)`, and `window(...)`; each takes the input list of dictionaries, lookup list, and request dictionary and returns a new list without mutating arguments. `lookup` is the lookup-enrichment family.

Requests support `fill` (`zero`, `mean`, `median`; default `zero`), `agg` (`sum`, `mean`, `count`; default `sum`), and `window` (2, 3, or 4). Missing units are filled globally before revenue calculation; all-missing units fill with zero. Region strings are stripped and lowercased. Aggregations ignore missing revenue, with empty sum/count zero and empty mean None. Group outputs are sorted by stringified keys. Lookup matches normalized region keys and returns `revenue_cents_per_target`, with None for missing/zero target or revenue.

Example: `revenue([{'region':' WEST ', 'units':2, 'price_cents':10}], [], {'fill':'zero'})` returns a copied row with region `west` and revenue_cents `20` (other supplied keys are retained).

Limitations: expects mappings with the documented field types; invalid fill/agg/window values raise ValueError. This package does not add schema validation.
