"""
factorial_calculator_1 - Calculates factorial of a number
Created by: Agent_03
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Calculate factorial of n"""
    try:
        n = int(parameters.get('n', 5))
        if n < 0:
            return {"success": False, "result": "Factorial undefined for negative numbers"}
        
        result = 1
        for i in range(1, n + 1):
            result *= i
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
