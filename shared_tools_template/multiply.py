"""
Multiply Tool - Basic multiplication that can be composed by other tools
Created by: system
Energy Reward: 8
"""

def execute(parameters, context=None):
    """
    Execute the multiply tool.
    
    Parameters:
        a (float): first number
        b (float): second number
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        a = float(parameters.get('a', 0))
        b = float(parameters.get('b', 0))
        
        result = a * b
        
        return {
            'success': True,
            'result': f'{a} * {b} = {result}',
            'numeric_result': result,  # For other tools to use
            'energy_gain': 8
        }
        
    except Exception as e:
        return {
            'success': False,
            'result': f'Multiplication error: {str(e)}',
            'energy_gain': 0
        } 