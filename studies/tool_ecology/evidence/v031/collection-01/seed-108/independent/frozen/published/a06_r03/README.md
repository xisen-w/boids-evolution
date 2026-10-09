# Row table transforms

Native Python package, no external dependencies. Public functions all accept `(rows, lookup, request)` and return new dictionaries without mutating inputs. `clean` normalizes non-null region strings and fills null units. `revenue` fills units and appends `revenue_cents`, preserving region exactly. `group` and `monthly` normalize regions and aggregate non-null revenue by region or `(date[:7], region)` respectively. `lookup` normalizes regions and appends the revenue/target ratio; `window` appends trailing-row mean revenue without changing regions. Fill is `zero`, `mean`, or `median` (all-null -> 0); aggregation is `sum`, `mean`, or `count`; windows are 2, 3, or 4. Empty means and unavailable lookup ratios are `None`; group count excludes missing revenues.

Example: `from candidate import revenue; revenue([{'units': 2, 'price_cents': 30}], [], {'fill':'zero'})[0]['revenue_cents'] == 60`.
