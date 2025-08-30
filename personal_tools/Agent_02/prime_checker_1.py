"""
prime_checker_1 - Checks if a number is prime
Created by: Agent_02
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Check if a number is prime"""
    try:
        n = int(parameters.get('n', 2))
        if n < 2:
            return {"success": True, "result": False}
        
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return {"success": True, "result": False}
        
        return {"success": True, "result": True}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
