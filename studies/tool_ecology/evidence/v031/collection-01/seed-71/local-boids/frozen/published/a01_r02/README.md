# Candidate row services

Native Python functions accept `(rows, lookup, request)` and return newly allocated row dictionaries without mutating inputs. Public APIs: `clean`, `revenue`, `group`, `monthly`, `lookup`, and `window`.

```python
from candidate import revenue, group
rows = [{'region':' North ', 'date':'2025-01-03', 'units':2, 'price_cents':150}]
revenue(rows, [], {'fill':'zero'}) # region north, revenue_cents 300
group(rows, [], {'fill':'zero', 'agg':'sum'})
```

Missing units use request `fill` (`zero`, `mean`, `median`; all-missing gives zero). Revenue is units times price or `None` if price is missing. Group and monthly aggregate nonmissing revenue by available keys; empty mean is `None`, sum/count are zero. Lookup adds revenue divided by exact normalized region target; unknown/zero/missing targets yield `None`. Window is a trailing ROWS mean including current, with width 2, 3, or 4. Aggregation uses `sum`, `mean`, or `count`. Region normalization strips whitespace and lowercases. Dates are grouped using their first seven characters; inputs otherwise are expected to contain numeric operands and valid request values. Original columns and order are preserved by row-oriented services.
