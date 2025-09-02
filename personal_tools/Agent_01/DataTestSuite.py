def execute(parameters, context=None):
    """Simple DataTestSuite execution function."""
    try:
        test_cases = parameters.get('test_cases', [])
        results = []
        for idx, case in enumerate(test_cases):
            input_data = case.get('input')
            transform_code = case.get('transform_code')
            expected_output = case.get('expected_output')
            # Execute transformation code
            local_vars = {}
            exec(transform_code, {}, local_vars)
            transform_func = local_vars.get('transform')
            if not transform_func:
                results.append({'test_case': idx, 'status': 'fail', 'reason': 'No transform function'})
                continue
            output = transform_func(input_data)
            # Validate output
            if output == expected_output:
                results.append({'test_case': idx, 'status': 'pass'})
            else:
                results.append({'test_case': idx, 'status': 'fail', 'output': output})
        return {'results': results}
    except Exception as e:
        return {'error': str(e)}