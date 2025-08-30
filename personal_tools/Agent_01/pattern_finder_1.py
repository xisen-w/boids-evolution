"""
pattern_finder_1 - Finds patterns in sequences
Created by: Agent_01
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Find arithmetic or geometric patterns"""
    try:
        sequence = parameters.get('sequence', [])
        if isinstance(sequence, str):
            sequence = [float(x.strip()) for x in sequence.split(',')]
        
        if len(sequence) < 2:
            return {"success": False, "result": "Need at least 2 numbers"}
        
        # Check arithmetic progression
        diff = sequence[1] - sequence[0]
        is_arithmetic = all(sequence[i] - sequence[i-1] == diff for i in range(1, len(sequence)))
        
        # Check geometric progression
        if sequence[0] != 0:
            ratio = sequence[1] / sequence[0] if sequence[0] != 0 else 0
            is_geometric = all(abs(sequence[i] / sequence[i-1] - ratio) < 0.001 for i in range(1, len(sequence)) if sequence[i-1] != 0)
        else:
            is_geometric = False
        
        result = {"arithmetic": is_arithmetic, "geometric": is_geometric}
        if is_arithmetic:
            result["arithmetic_diff"] = diff
        if is_geometric:
            result["geometric_ratio"] = ratio
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
