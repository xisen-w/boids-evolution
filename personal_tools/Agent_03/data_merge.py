def execute(parameters, context=None):
    """Merge multiple datasets with specified join options."""
    import pandas as pd
    try:
        datasets = parameters.get('datasets')
        on = parameters.get('on')
        how = parameters.get('how', 'inner')
        suffixes = parameters.get('suffixes', ('_x', '_y'))
        merge_index = parameters.get('merge_index', False)

        if not datasets or len(datasets) < 2:
            return {"error": "At least two datasets are required."}
        merged_df = datasets[0]
        for df in datasets[1:]:
            if merge_index:
                merged_df = pd.merge(merged_df, df, left_index=True, right_index=True, how=how, suffixes=suffixes)
            else:
                merged_df = pd.merge(merged_df, df, on=on, how=how, suffixes=suffixes)
        return {"result": merged_df}
    except Exception as e:
        return {"error": str(e)}