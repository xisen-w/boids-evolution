"""
Calculate Tool - Perform mathematical calculations
Created by: system
"""

def execute(parameters, context=None):
    """
    Execute the calculate tool.
    
    Parameters:
        operation (str): add, subtract, multiply, divide
        a (float): first number
        b (float): second number
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        operation = parameters.get('operation', 'add')
        a = float(parameters.get('a', 0))
        b = float(parameters.get('b', 0))
        
        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                return {
                    'success': False,
                    'result': 'Division by zero error',
                    'energy_gain': 0
                }
            result = a / b
        else:
            return {
                'success': False,
                'result': f'Unknown operation: {operation}',
                'energy_gain': 0
            }
        
        return {
            'success': True,
            'result': f'{a} {operation} {b} = {result}',
            'energy_gain': 10
        }
        
    except Exception as e:
        return {
            'success': False,
            'result': f'Calculation error: {str(e)}',
            'energy_gain': 0
        } 