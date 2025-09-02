def execute(parameters, context=None):
    import pandas as pd
    import numpy as np

    try:
        data = parameters.get('data')
        if isinstance(data, str):
            if data.endswith('.csv'):
                df = pd.read_csv(data)
            elif data.endswith('.json'):
                df = pd.read_json(data)
            else:
                return {"error": "Unsupported file format"}
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            return {"error": "Invalid data input"}

        # Handle missing data
        method = parameters.get('missing_method', 'drop')
        fill_value = parameters.get('fill_value', None)
        cols = parameters.get('columns', df.columns)
        if method == 'drop':
            df.dropna(subset=cols, inplace=True)
        elif method in ['mean', 'median', 'mode']:
            for col in cols:
                if df[col].isnull().any():
                    if method == 'mean':
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif method == 'median':
                        df[col].fillna(df[col].median(), inplace=True)
                    elif method == 'mode':
                        df[col].fillna(df[col].mode()[0], inplace=True)
        elif fill_value is not None:
            df[cols] = df[cols].fillna(fill_value)

        # Detect outliers
        outlier_method = parameters.get('outlier_method', 'iqr')
        outlier_action = parameters.get('outlier_action', 'remove')
        for col in df.select_dtypes(include=[np.number]).columns:
            if outlier_method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
                mask = (df[col] < lower) | (df[col] > upper)
                if outlier_action == 'remove':
                    df = df[~mask]
                elif outlier_action == 'cap':
                    df.loc[mask, col] = np.where(df.loc[mask, col] > upper, upper, lower)

        # Normalize or standardize
        norm_type = parameters.get('norm_type', None)