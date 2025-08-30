"""
statistics_calculator_1 - Calculates basic statistics
Created by: Agent_03
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Calculate mean, median, mode of data"""
    try:
        data = parameters.get('data', [])
        if isinstance(data, str):
            data = [float(x.strip()) for x in data.split(',')]
        elif isinstance(data, list):
            data = [float(x) for x in data]
        
        if not data:
            return {"success": False, "result": "No data provided"}
        
        mean = sum(data) / len(data)
        sorted_data = sorted(data)
        n = len(sorted_data)
        median = sorted_data[n//2] if n % 2 == 1 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        
        return {"success": True, "result": {"mean": mean, "median": median, "count": n}}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
