"""
list_sorter_1 - Sorts a list of numbers
Created by: Agent_04
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Sort a list of numbers"""
    try:
        data = parameters.get('data', [])
        if isinstance(data, str):
            data = [float(x.strip()) for x in data.split(',')]
        elif isinstance(data, list):
            data = [float(x) for x in data]
        
        sorted_data = sorted(data)
        return {"success": True, "result": sorted_data}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
