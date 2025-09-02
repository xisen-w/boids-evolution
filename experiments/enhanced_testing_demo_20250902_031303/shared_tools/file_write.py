"""
File Write Tool - Write content to files
Created by: system
"""

import os
from datetime import datetime

def execute(parameters, context=None):
    """
    Execute the file_write tool.
    
    Parameters:
        filename (str): name of the file (optional)
        content (str): content to write
        context (ToolExecutionContext): execution context for calling other tools
    
    Returns:
        dict: {'success': bool, 'result': str, 'energy_gain': int}
    """
    try:
        filename = parameters.get('filename', f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        content = parameters.get('content', '')
        
        # Ensure agent_outputs directory exists
        output_dir = "agent_outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return {
            'success': True,
            'result': f'Successfully wrote content to {filepath}',
            'energy_gain': 15
        }
        
    except Exception as e:
        return {
            'success': False,
            'result': f'File write error: {str(e)}',
            'energy_gain': 0
        } 