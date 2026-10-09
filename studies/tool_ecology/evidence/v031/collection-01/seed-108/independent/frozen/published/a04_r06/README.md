# Row-table services

Import the package and call any public function with `(rows, lookup, request)`:
`candidate.clean(rows, lookup, {"fill": "median"})`. The six public adapters are
`clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`. They implement the
service contracts for normalization/filling, revenue derivation, region and
month-region aggregates, exact-key target lookup, and trailing-row revenue means.
For example: `candidate.group(rows, [], {"fill": "zero", "agg": "sum"})`.

The functions return new outputs and leave inputs unchanged. Fill is selected
through request.fill (`zero`, `mean`, or `median`); aggregation through
request.agg (`sum`, `mean`, or `count`); rolling width through request.window
(2, 3, or 4). Input schemas and missing-value behavior follow the stated service
contracts. This package delegates to the verified `a04_r05` implementation and
requires that declared dependency to be available.
