# Multi-service table dispatcher

This package reuses the verified native table operations from `a04_r05` and
adds `run_many(families, rows, lookup_rows, request)`, returning a dictionary
mapping each requested family to its normal full service result. Example:

```python
from candidate import run_many
results = run_many(['clean', 'window'], rows, [],
                   {'fill': 'median', 'window': 3})
```

Supported names: `clean`, `revenue`, `group`, `monthly`, `lookup`, `window`.
Unknown names raise `ValueError`. Calls operate independently on original
inputs (results are not chained); repeated names overwrite the same dictionary
key. The package also exports thin `*_service(rows, lookup_rows, request)`
adapters for each family. Output schemas and edge cases match the referenced
services; input schema validation is not added here.
