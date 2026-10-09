# Table services

Import `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window` from this package. Each public function accepts `(rows, lookup, request)` and returns a new list of dictionaries; input objects are not mutated. `lookup` argument is used only by the lookup service.

* `clean`: strips/lowercases region and fills null units using `request['fill']` (`zero`, `mean`, or `median`; default `zero`).
* `revenue`: fills units and appends `revenue_cents`; region is left untouched.
* `group`: normalized region groups; `request['agg']` supports `sum`, `mean`, `count` (default `sum`).
* `monthly`: groups by date month and normalized region, using the same aggregations.
* `lookup`: appends `revenue_cents_per_target` based on normalized exact region keys.
* `window`: appends mean revenue over trailing rows; `request['window']` must be 2, 3, or 4.

Example: `revenue([{'units': None, 'price_cents': 4, 'region': ' X '}], [], {'fill':'zero'})` returns a row with units 0 and revenue_cents 0, retaining region as `' X '`. Missing arithmetic inputs yield `None`; all-missing fill uses zero. Aggregates omit missing revenue. Input records are expected to be dictionaries and request values must be supported options.
