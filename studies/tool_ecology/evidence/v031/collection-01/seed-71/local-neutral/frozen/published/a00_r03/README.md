# Table service adapters

Dependency-light public adapters delegating to the received, host-verified
`published.a00_r02` implementation. Import with `from candidate import clean,
revenue, group, monthly, lookup_service, window`. Every adapter has the exact
signature `(rows, lookup, request)` and returns a new list (and new row dicts);
inputs are not mutated. `lookup_service` is named thus to distinguish the lookup
table argument from the service itself.

* `clean(rows, lookup, request)`: normalize string regions with strip/lower and
  fill missing `units`; `request['fill']` is `zero`, `mean`, or `median`.
* `revenue(...)`: same fill behavior and append `revenue_cents = units *
  price_cents` (None if either is missing).
* `group(...)`: normalized region aggregation, dropping missing regions.
* `monthly(...)`: aggregation by `date[:7]` and normalized region, dropping
  either missing key. For both aggregation APIs `request['agg']` is `sum`,
  `mean`, or `count`; count excludes missing revenue. Output keys are sorted by
  their string representations; empty sum/count groups produce 0.
* `lookup_service(...)`: normalize region, derive revenue, and append
  `revenue_cents_per_target`. Lookup matches exact region after strip/lower;
  unknown region, absent/zero target, or missing revenue yields None. Lookup
  metadata is not added to result rows.
* `window(...)`: derive revenue and append `roll_revenue_cents`, the mean of
  nonmissing revenue in the trailing `request['window']` rows including current.
  Missing values do not extend the row window.

Example: `revenue([{'units': 2, 'price_cents': 5}], [], {'fill': 'zero'})`
returns `[{'units': 2, 'price_cents': 5, 'revenue_cents': 10}]`.
An all-missing units column fills with 0. Parameters are expected to use the
listed values; date strings are expected in ISO `YYYY-MM-DD` form.
