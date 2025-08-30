"""
boolean_evaluator_1 - Evaluates boolean expressions
Created by: Agent_04
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Evaluate boolean expression"""
    try:
        expr = str(parameters.get('expression', 'True'))
        # Simple boolean evaluation
        expr = expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not ')
        
        # Safe evaluation
        allowed_names = {"True": True, "False": False, "and": lambda x, y: x and y, "or": lambda x, y: x or y, "not": lambda x: not x}
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
