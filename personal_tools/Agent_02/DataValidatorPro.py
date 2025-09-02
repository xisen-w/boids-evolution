def execute(parameters, context=None):
    """Simple DataValidatorPro function: checks for missing values and data types."""
    try:
        data = parameters.get('data')
        schema = parameters.get('schema', {})
        report = {'missing_values': {}, 'type_mismatches': {}}
        if data is None or not isinstance(data, dict):
            return {'error': 'Invalid or missing data'}
        for field, rules in schema.items():
            value = data.get(field)
            # Check missing
            if value is None:
                report['missing_values'][field] = 'Missing'
            else:
                # Check type
                expected_type = rules.get('type')
                if expected_type and not isinstance(value, eval(expected_type)):
                    report['type_mismatches'][field] = f'Expected {expected_type}, got {type(value).__name__}'
        return {'validation_report': report}
    except Exception as e:
        return {'error': str(e)}