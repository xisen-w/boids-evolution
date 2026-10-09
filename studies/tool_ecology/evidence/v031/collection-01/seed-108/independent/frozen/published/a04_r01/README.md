# Tabular service functions

Native Python, no dependencies. Public API: `clean(rows, lookup, request)`, `revenue(rows, lookup, request)`, `group(rows, lookup, request)`, `monthly(rows, lookup, request)`, `lookup(rows, lookup_rows, request)`, and `window(rows, lookup, request)`. Each accepts a list of row dictionaries, lookup rows (ignored except by lookup), and request dictionary, and returns a new list without mutating inputs. Region values are stripped and lowercased; missing units are filled using request `fill` (`zero`, `mean`, `median`; all missing becomes zero). Revenue adds `revenue_cents`. Group/monthly support `agg` (`sum`, `mean`, `count`) and drop missing grouping keys; count excludes missing revenues. Monthly uses the first seven date characters. Lookup adds `revenue_cents_per_target`, matching normalized regions; unknown, missing, or zero targets produce None. Window adds the trailing row-window mean using request `window` (default 2), ignoring missing revenues and returning None for an empty window.

Example: `revenue([{'region':' North ','units':2,'price_cents':50}], [], {'fill':'zero'})` returns `[{'region':'north','units':2,'price_cents':50,'revenue_cents':100}]`.

Input dates are expected to be ISO-like strings; only their first seven characters are used. Aggregation defaults to sum, and unknown fill modes fall back to zero.
