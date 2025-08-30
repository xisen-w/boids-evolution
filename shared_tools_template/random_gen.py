"""
Random Generator Tool - Generate random numbers or choices
Created by: system
"""

import random

def execute(parameters, context=None):
    """
    Execute the random_gen tool.
    
    Parameters:
        type (str): 'number' or 'choice'
        min (int): minimum value (for type='number')
        max (int): maximum value (for type='number')
        choices (list): list of options (for type='choice')
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        gen_type = parameters.get('type', 'number')
        
        if gen_type == 'number':
            min_val = int(parameters.get('min', 1))
            max_val = int(parameters.get('max', 100))
            result = random.randint(min_val, max_val)
            return {
                'success': True,
                'result': f'Random number between {min_val} and {max_val}: {result}',
                'energy_gain': 5
            }
        
        elif gen_type == 'choice':
            choices = parameters.get('choices', ['option1', 'option2', 'option3'])
            result = random.choice(choices)
            return {
                'success': True,
                'result': f'Random choice from {choices}: {result}',
                'energy_gain': 5
            }
        
        else:
            return {
                'success': False,
                'result': f'Unknown random type: {gen_type}',
                'energy_gain': 0
            }
            
    except Exception as e:
        return {
            'success': False,
            'result': f'Random generation error: {str(e)}',
            'energy_gain': 0
        } 