# Row services

Native, non-mutating table adapters. Import `clean`, `revenue`, `group`, `monthly`, `lookup`, or `window` from `candidate`; each accepts `(rows, lookup, request)`. Rows and lookup are lists of mappings; request is a mapping. Example: `revenue([{'units': 2, 'price_cents': 50}], [], {'fill':'zero'})[0]['revenue_cents'] == 100`.

`clean` normalizes region and fills missing units. `revenue` fills units and adds revenue without altering other input columns. Group and monthly normalize regions, derive revenue, and aggregate as requested. Lookup adds the ratio using normalized region keys; window adds the trailing ROWS mean. Fill methods are zero/mean/median (all missing -> zero); aggregate methods are sum/mean/count. Window is 2, 3, or 4. Missing revenue is excluded from aggregates; mean with no values is None. No adapter mutates inputs. Assumes numeric values and ISO-like date strings; malformed parameters raise ValueError where validated.
