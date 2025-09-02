def execute(parameters, context=None):
    """Performs grouping and aggregation on dataset."""
    import pandas as pd
    try:
        data = parameters.get('data')
        group_keys = parameters.get('group_keys', [])
        aggregations = parameters.get('aggregations', {})
        if data is None or not isinstance(data, list):
            return {"error": "Invalid or missing data"}
        df = pd.DataFrame(data)
        # Validate columns
        for col in group_keys:
            if col not in df.columns:
                return {"error": f"Group key column '{col}' not found"}
        for col in aggregations:
            if col not in df.columns:
                return {"error": f"Aggregation target column '{col}' not found"}
        # Validate aggregation functions
        valid_funcs = {'sum', 'mean', 'count', 'max', 'min'}
        for funcs in aggregations.values():
            if not isinstance(funcs, list):
                return {"error": "Aggregations should be a list of functions"}
            for f in funcs:
                if f not in valid_funcs:
                    return {"error": f"Unsupported aggregation function '{f}'"}
        # Prepare aggregation dict for pandas
        agg_dict = {}
        for col, funcs in aggregations.items():
            agg_dict[col] = funcs
        grouped = df.groupby(group_keys).agg(agg_dict)
        # Flatten MultiIndex columns if needed
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
        result = grouped.reset_index().to_dict(orient='records')
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}