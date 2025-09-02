def execute(parameters, context=None):
    """Validate dataset against rules, checking for missing values, outliers, and schema violations."""
    try:
        data = parameters.get('data')
        rules = parameters.get('rules', {})
        report = {'issues': [], 'status': 'pass'}
        if data is None or not hasattr(data, 'columns'):
            return {'error': 'Invalid or missing data'}
        # Schema validation
        schema = rules.get('schema', {})
        for col, dtype in schema.items():
            if col not in data.columns:
                report['issues'].append(f"Missing column: {col}")
                report['status'] = 'fail'
            elif not pd.api.types.is_dtype_equal(data[col].dtype, dtype):
                report['issues'].append(f"Type mismatch in {col}")
                report['status'] = 'fail'
        # Missing values check
        for col in data.columns:
            missing = data[col].isnull().sum()
            if missing > 0:
                report['issues'].append(f"{missing} missing in {col}")
                report['status'] = 'fail'
        # Outlier detection (z-score)
        import numpy as np
        for col in data.select_dtypes(include=[np.number]).columns:
            mean = data[col].mean()
            std = data[col].std()
            if std == 0:
                continue
            z_scores = (data[col] - mean) / std
            outliers = data[np.abs(z_scores) > 3]
            if not outliers.empty:
                report['issues'].append(f"Outliers detected in {col}")
                report['status'] = 'fail'
        return {'report': report}
    except Exception as e:
        return {'error': str(e)}