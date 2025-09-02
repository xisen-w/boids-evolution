"""
Power Tool - Calculates power using repeated multiplication (complex composition)
Created by: system
"""

def execute(parameters, context=None):
    """
    Execute the power tool using repeated multiplication.
    
    This demonstrates complex tool composition where one tool calls another
    multiple times. Shows how complex operations can emerge from simple building blocks.
    
    Parameters:
        base (float): base number
        exponent (int): exponent (must be positive integer)
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        base = float(parameters.get('base', 0))
        exponent = int(parameters.get('exponent', 1))
        
        if exponent < 0:
            return {
                'success': False,
                'result': 'Negative exponents not supported',
                'energy_gain': 0
            }
        
        if exponent == 0:
            return {
                'success': True,
                'result': f'{base}^0 = 1',
                'numeric_result': 1,
                'energy_gain': 15
            }
        
        if exponent == 1:
            return {
                'success': True,
                'result': f'{base}^1 = {base}',
                'numeric_result': base,
                'energy_gain': 15
            }
        
        # Check if we have context to call other tools
        if context is None:
            # Fallback to direct calculation
            result = base ** exponent
            return {
                'success': True,
                'result': f'{base}^{exponent} = {result} (direct calculation)',
                'numeric_result': result,
                'energy_gain': 15
            }
        
        # Use repeated multiplication for composition
        result = base
        multiply_operations = []
        
        for i in range(exponent - 1):
            multiply_result = context.call_tool('multiply', {'a': result, 'b': base})
            
            if multiply_result['success']:
                result = multiply_result.get('numeric_result', result)
                multiply_operations.append(f'multiply({result}, {base})')
            else:
                # Fallback to direct calculation if multiply fails
                result = base ** exponent
                return {
                    'success': True,
                    'result': f'{base}^{exponent} = {result} (fallback after multiply failed at step {i+1})',
                    'numeric_result': result,
                    'energy_gain': 10,  # Lower reward for fallback
                    'fallback_reason': f'multiply tool failed at iteration {i+1}'
                }
        
        return {
            'success': True,
            'result': f'{base}^{exponent} = {result} (using {exponent-1} multiply operations)',
            'numeric_result': result,
            'energy_gain': 15,
            'composition': f'power({base}, {exponent}) = ' + ' -> '.join(multiply_operations),
            'operations_count': exponent - 1
        }
        
    except Exception as e:
        return {
            'success': False,
            'result': f'Power calculation error: {str(e)}',
            'energy_gain': 0
        } 