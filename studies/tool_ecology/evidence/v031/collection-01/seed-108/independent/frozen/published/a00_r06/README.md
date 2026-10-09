# Row transforms

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`. Each callable accepts `(rows, lookup, request)` where rows and lookup are lists of dictionaries and request is a dict. Results are fresh rows; inputs remain unchanged.

Example: `from candidate import revenue; revenue([{'units': 2, 'price_cents': 50}], [], {'fill': 'zero'})[0]['revenue_cents'] == 100`.

Fill choices: zero, mean, median; all missing units fill to zero. Aggregations: sum, mean, count. Window widths: 2, 3, 4. Clean normalizes region and fills units; revenue derives revenue; group/monthly aggregate; lookup adds per-target revenue; window adds trailing-row mean. Exact details and limitations follow required dependency `published.a00_r02`.
