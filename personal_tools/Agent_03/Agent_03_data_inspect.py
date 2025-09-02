def execute(parameters, context=None):
    """Inspect a pandas DataFrame: shape, data types, missing values, stats, unique counts."""
    import pandas as pd
    try:
        data = parameters.get('data')
        if not isinstance(data, pd.DataFrame):
            return {"error": "Input is not a pandas DataFrame."}
        shape = data.shape
        dtypes = data.dtypes.to_dict()
        missing = data.isnull().sum().to_dict()
        numeric_cols = data.select_dtypes(include='number').columns
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "mean": data[col].mean(),
                "median": data[col].median(),
                "min": data[col].min(),
                "max": data[col].max()
            }
        unique_counts = data.nunique().to_dict()
        sample_rows = data.head().to_dict(orient='records')
        return {
            "shape": shape,
            "dtypes": dtypes,
            "missing_values": missing,
            "numeric_stats": stats,
            "unique_counts": unique_counts,
            "sample_rows": sample_rows
        }
    except Exception as e:
        return {"error": str(e)}