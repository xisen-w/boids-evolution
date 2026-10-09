# a02_r04

Native Python implementations of the six table service families. Public adapters are `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup_service(rows, lookup, request)`, and `window(rows, lookup, request)`; each returns a new list and does not mutate inputs. `request` requires `fill` (`zero`, `mean`, `median`), and aggregate services additionally require `agg` (`sum`, `mean`, `count`); window requires `window` (row count).

Clean preserves source columns and order while normalizing region and filling units. Revenue adds `revenue_cents`; group/monthly return sorted aggregate rows; lookup adds `revenue_cents_per_target` using exact normalized-region keys; window adds trailing row-window `roll_revenue_cents`. Missing values and empty aggregate groups follow the service contract. Lookup manager and target fields are not appended to output.

Example: `revenue([{'region':' West ', 'units':None, 'price_cents':5}], [], {'fill':'zero'})` returns a copied row with region `west`, units `0`, and revenue_cents `0`.
