# Tabular service adapters

Dependency-free Python adapters for the six row-table services. Each public adapter has signature `(rows, lookup, request)`; inputs are not mutated. Inputs are lists of dictionaries and results are fresh dictionaries. Import with `from candidate import clean, revenue, group, monthly, lookup, window`.

```python
rows = [{'region': ' West ', 'date': '2024-01-05', 'units': None, 'price_cents': 20}]
clean(rows, [], {'fill': 'zero'})[0]['region']  # 'west'
revenue(rows, [], {'fill': 'zero'})[0]['revenue_cents']  # 0
```

Fill methods are `zero`, `mean`, and `median`; all-missing units fill with zero, and even medians average the middle pair. Group/monthly aggregation accepts `sum`, `mean`, and `count`; missing revenue values are excluded and missing group keys dropped. Lookup normalizes region keys and emits `revenue_cents_per_target`; unknown, missing or zero targets produce None. Window takes a trailing ROWS count from request.window and averages nonmissing revenues within those rows. Clean, group, monthly and lookup normalize region; revenue and window preserve region as provided. Monthly expects ISO date strings and takes the first seven characters. Values are expected to follow the documented service schema.
