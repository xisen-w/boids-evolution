def execute(parameters, context=None):
    """Data cleaning utility for handling missing values, outliers, scaling, and data types."""
    import pandas as pd
    import numpy as np

    try:
        data = parameters.get('dataset')
        missing_strategy = parameters.get('missing_strategy', 'drop')
        fill_value = parameters.get('fill_value', None)
        detect_outliers = parameters.get('detect_outliers', False)
        outlier_method = parameters.get('outlier_method', 'z_score')
        outlier_threshold = parameters.get('outlier_threshold', 3)
        standardize = parameters.get('standardize', False)
        normalize = parameters.get('normalize', False)
        data_types = parameters.get('data_types', {})

        # Handle missing data
        if missing_strategy == 'drop':
            data = data.dropna()
        elif missing_strategy.startswith('fill'):
            if missing_strategy == 'fill_mean':
                data = data.fillna(data.mean())
            elif missing_strategy == 'fill_median':
                data = data.fillna(data.median())
            elif missing_strategy == 'fill_mode':
                data = data.fillna(data.mode().iloc[0])
            elif missing_strategy == 'fill_constant' and fill_value is not None:
                data = data.fillna(fill_value)

        # Detect and handle outliers
        if detect_outliers:
            for col in data.select_dtypes(include=[np.number]).columns:
                col_data = data[col]
                if outlier_method == 'z_score':
                    z_scores = (col_data - col_data.mean()) / col_data.std()
                    mask = z_scores.abs() > outlier_threshold
                elif outlier_method == 'IQR':
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    mask = (col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)
                data = data[~mask]

        # Standardize or normalize
        num_cols = data.select_dtypes(include=[np.number]).columns
        if standardize:
            data[num_cols] = (data[num_cols] - data[num_cols].mean()) / data[num_cols].std()
        elif normalize:
            data[num_cols] = (data[num_cols] - data[num