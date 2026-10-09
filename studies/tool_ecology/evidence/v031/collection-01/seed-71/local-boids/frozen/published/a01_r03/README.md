# Row-table sales services

This package exposes six pure adapters, each with signature
`function(rows, lookup, request)`: `clean`, `revenue`, `group`, `monthly`,
`lookup` and `window`. Inputs are list-of-dict rows and lookup records; functions
return fresh results and do not mutate inputs. `request.fill` accepts `zero`,
`mean`, or `median` (default `zero`); `request.agg` accepts `sum`, `mean`, or
`count`; `request.window` accepts 2, 3, or 4 (default 2).

Example: `revenue(rows, [], {'fill': 'median'})` fills missing units and adds
`revenue_cents`. Grouping services return aggregate rows; row services preserve
input row order and columns while adding their documented derived fields.
Missing values and empty input are supported per service contract. Invalid
parameter values raise `ValueError`. Numeric fields are expected to be numeric;
this API does not coerce strings or validate schemas.
