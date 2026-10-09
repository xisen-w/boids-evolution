# Row services

Native Python; no external dependencies. All APIs take `(rows, lookup, request)` and return new dictionaries without mutating inputs. Exports: `clean`, `revenue`, `group`, `monthly`, `lookup_service`, `window`.

`clean` fills missing units per `request['fill']` (`zero`, `mean`, `median`; defaults to `zero`) and normalizes region. `revenue` fills units and adds `revenue_cents`, preserving region verbatim. `group` and `monthly` normalize region, derive revenue and aggregate using `request['agg']` (`sum`, `mean`, `count`; defaults sum). Monthly uses first seven date characters. `lookup_service` normalizes region and adds per-target revenue using lookup region/target. `window` adds trailing row mean for widths 2, 3, or 4.

Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})` returns `[{'units': 2, 'price_cents': 50, 'revenue_cents': 100}]`. All-missing units fill with zero. Aggregation drops null revenues; mean of no values is `None`, while sum/count are zero. Lookup is named `lookup_service` to avoid shadowing the input argument conceptually.
