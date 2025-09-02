def execute(parameters, context=None):
    """Execute a list of test cases, compare outputs, and generate a report."""
    test_cases = parameters.get('test_cases', [])
    report = {
        'total': len(test_cases),
        'passed': 0,
        'failed': [],
    }
    for idx, case in enumerate(test_cases):
        func = case.get('function')
        input_data = case.get('input')
        expected = case.get('expected')
        try:
            output = func(input_data)
            if output == expected:
                report['passed'] += 1
            else:
                report['failed'].append({
                    'test_case': idx + 1,
                    'input': input_data,
                    'expected': expected,
                    'actual': output
                })
        except Exception as e:
            report['failed'].append({
                'test_case': idx + 1,
                'input': input_data,
                'expected': expected,
                'error': str(e)
            })
    return report