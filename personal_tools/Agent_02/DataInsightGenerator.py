def execute(parameters, context=None):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    data = parameters.get('data')
    columns = parameters.get('columns', data.columns if hasattr(data, 'columns') else None)
    show_plots = parameters.get('show_plots', True)
    outlier_method = parameters.get('outlier_method', 'iqr')
    outlier_threshold = parameters.get('outlier_threshold', 1.5)

    try:
        if not isinstance(data, pd.DataFrame):
            return {"error": "Input data must be a pandas DataFrame."}
        report = {}
        # Validation
        missing = data.isnull().sum()
        report['missing_values'] = missing.to_dict()
        # Descriptive stats
        desc = data.describe(include='all')
        report['descriptive_stats'] = desc.to_dict()
        # Outlier detection
        outliers = {}
        for col in columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                q1 = data[col].quantile(0.25)
                q3 = data[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - outlier_threshold * iqr
                upper = q3 + outlier_threshold * iqr
                outlier_mask = (data[col] < lower) | (data[col] > upper)
                outliers[col] = {
                    'count': outlier_mask.sum(),
                    'percentage': outlier_mask.mean() * 100
                }
        report['outliers'] = outliers
        # Visualization
        if show_plots:
            for col in columns:
                if pd.api.types.is_numeric_dtype(data[col]):
                    plt.figure()
                    data[col].hist()
                    plt.title(f'Histogram of {col}')
                    plt.show()
        return report
    except Exception as e:
        return {"error": str(e)}