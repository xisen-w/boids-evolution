# Native table services

Root API: `clean(rows, lookup, request)`, `revenue(...)`, `group(...)`,
`monthly(...)`, `lookup(...)`, and `window(...)`. Each accepts a list of
row dictionaries, lookup-row list, and request dictionary and returns new
row dictionaries without changing inputs. Missing unit fill supports `zero`,
`mean`, and `median`; aggregation supports `sum`, `mean`, and `count`.

Example: `group(rows, [], {'fill':'mean','agg':'sum'})` returns dictionaries
with `region` and `sum_revenue_cents`. Regions are stripped/lowercased;
monthly keys derive from the first seven characters of date. Window sizes are
provided in `request['window']`, with trailing rows including the current row.
Unknown lookup targets, zero targets, and absent revenue produce a null ratio.
