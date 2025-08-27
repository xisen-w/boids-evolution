"""
Square Tool - Squares a number using the multiply tool (demonstrates composition)
Created by: system
Energy Reward: 12
"""

def execute(parameters, context=None):
    """
    Execute the square tool by calling the multiply tool.
    
    This demonstrates tool composition - one tool calling another.
    The creator of the multiply tool gets utility rewards when this runs.
    
    Parameters:
        number (float): number to square
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        number = float(parameters.get('number', 0))
        
        # Check if we have context to call other tools
        if context is None:
            # Fallback to direct calculation if no context
            result = number * number
            return {
                'success': True,
                'result': f'Square of {number} = {result} (direct calculation)',
                'numeric_result': result,
                'energy_gain': 12
            }
        
        # Use the multiply tool for composition
        multiply_result = context.call_tool('multiply', {'a': number, 'b': number})
        
        if multiply_result['success']:
            return {
                'success': True,
                'result': f'Square of {number} = {multiply_result.get("numeric_result", "unknown")} (using multiply tool)',
                'numeric_result': multiply_result.get('numeric_result'),
                'energy_gain': 12,
                'composition': f'square({number}) = multiply({number}, {number})'
            }
        else:
            # Fallback if multiply tool fails
            result = number * number
            return {
                'success': True,
                'result': f'Square of {number} = {result} (fallback after multiply failed)',
                'numeric_result': result,
                'energy_gain': 8,  # Lower reward for fallback
                'fallback_reason': multiply_result.get('result', 'multiply tool failed')
            }
        
    except Exception as e:
        return {
            'success': False,
            'result': f'Square calculation error: {str(e)}',
            'energy_gain': 0
        } 