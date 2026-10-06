"""Public API specification, shared by every builder condition.

No reference code, sampled parameter values, probe tables, seeds, or answers.
Parameter domains describe the reusable interface, not the hidden test draws.
"""
PUBLIC_PRIMITIVES = {
    'filter': ('col,op,value', 'op is >, <, or ==; value is numeric. Keep matching rows in input order; drop missing col values.'),
    'fill_missing': ('col,strategy', 'strategy is zero, mean, or median of nonmissing values. Even-size median averages its two middle values; no nonmissing values means fill 0.'),
    'drop_missing': ('col', 'Drop rows with missing col; keep the order of remaining rows.'),
    'dedupe': ('key', 'Keep the first row for each key value, preserving input order.'),
    'derive': ('new,a,op,b', 'op is *, -, or +. Set new to the row-wise operation on a and b, or None if either is missing.'),
    'unit_convert': ('col,factor', 'Multiply nonmissing col values by the numeric factor; keep missing values.'),
    'month_bucket': ('col', 'Add month as YYYY-MM from the ISO date in col; missing/empty date gives None.'),
    'group_agg': ('key,col,agg', 'agg is sum, mean, count, or max. Drop missing keys; aggregate nonmissing col values. Output only key and <agg>_<col>, ordered by string form of key. Empty-value groups have sum/count 0 and mean/max None.'),
    'sort': ('col,desc', 'desc is True or False. Stable numeric sort; missing col values always last, in their original order.'),
    'top_k': ('col,k', 'Positive integer k. Take the first k rows of a stable descending sort with missing values last; do not drop missing rows before slicing.'),
    'zscore': ('col', 'Replace nonmissing col values using population standard deviation. Zero deviation gives 0; missing remains missing.'),
    'clip': ('col,lo,hi', 'Clamp each nonmissing value to the numeric interval [lo,hi]; missing remains missing.'),
    'join_lookup': ('key', 'Exact left join against the lookup list of rows. Add/overwrite its non-key columns; unmatched rows get None for those columns. Preserve input row order.'),
    'rank': ('col', 'Stable descending sort, missing last. Add rank_<col> as sequential 1-based float position, not dense/tied rank; missing values get rank None.'),
    'normalize_str': ('col', 'Strip whitespace and lowercase strings in col; nonstrings and missing values are unchanged.'),
    'cumsum': ('col', 'Add cumsum_<col> as running sum in input order. Missing contributes 0 and receives the current cumulative sum.'),
    'diff': ('col', 'Add diff_<col> as current minus previous NON-missing value. First nonmissing and missing rows get None; missing rows do not reset the previous value.'),
    'pct_of_total': ('col', 'Add pct_<col> = 100 * value / sum of nonmissing col values. Missing value or zero total gives None.'),
    'bin': ('col,edges', 'edges is a numeric list. Add bin_<col> as the float count of edges <= value; missing gives None.'),
    'rolling_mean': ('col,window', 'Positive integer window counts row positions, including current row. Add roll_<col> as mean of nonmissing values in that trailing window; empty window of values gives None.'),
    'multi_group_agg': ('keys,col,agg', 'keys is a list of column names; agg is sum, count, or mean. Drop rows missing any key. Aggregate nonmissing values and output only key columns and <agg>_<col>, sorted lexicographically by string forms of keys. Empty-value sum/count is 0, mean is None.'),
    'lookup_ratio': ('col', 'Add <col>_per_target = value / target from the lookup row with exactly matching region. Do not normalize implicitly. Missing value, unmatched region, or zero/missing target gives None.'),
}


def render_public_contract():
    header = ('Reusable primitive API contract: IMPLEMENTS means the whole interface, '
              'including all listed parameter variants, not just values appearing in this menu. '
              'Do not hard-code one operator or one column. Copy rows; preserve existing columns '
              'and row order except where the API explicitly changes them. '
              'These are functional specifications, not implementations.\n')
    return header + '\n'.join(f'- {name}({params}): {spec}'
                              for name, (params, spec) in PUBLIC_PRIMITIVES.items())
