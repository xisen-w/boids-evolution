def execute(parameters, context=None):
    """Calculate the mean (average) of a list of numbers."""
    try:
        numbers = parameters.get('numbers')
        if not isinstance(numbers, list):
            return {"error": "Parameter 'numbers' must be a list."}
        if len(numbers) == 0:
            return {"error": "The list 'numbers' is empty."}
        total = 0
        count = 0
        for num in numbers:
            if not isinstance(num, (int, float)):
                return {"error": "All elements in 'numbers' must be numeric."}
            total += num
            count += 1
        mean = total / count
        return {"mean": mean}
    except Exception as e:
        return {"error": str(e)}