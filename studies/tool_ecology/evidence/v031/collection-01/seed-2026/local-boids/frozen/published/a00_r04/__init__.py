"""Correct, non-mutating region-target enrichment service."""
from statistics import mean, median


def lookup(rows, lookup_rows, request):
    """Return copied rows with filled units, revenue_cents, and target rate.

    Region strings are stripped/lowercased on data rows; lookup keys are matched
    exactly to that normalized value. Missing/zero targets yield a None rate.
    """
    values = [r.get('units') for r in rows if r.get('units') is not None]
    mode = request.get('fill', 'zero')
    fill = mean(values) if mode == 'mean' and values else median(values) if mode == 'median' and values else 0
    targets = {item.get('region'): item.get('target') for item in lookup_rows}
    output = []
    for source in rows:
        row = dict(source)
        units = source.get('units')
        if units is None:
            units = fill
        row['units'] = units
        price = source.get('price_cents')
        revenue = None if units is None or price is None else units * price
        row['revenue_cents'] = revenue
        region = source.get('region')
        region = region.strip().lower() if isinstance(region, str) else region
        target = targets.get(region)
        row['revenue_cents_per_target'] = None if revenue is None or target is None or target == 0 else revenue / target
        output.append(row)
    return output
