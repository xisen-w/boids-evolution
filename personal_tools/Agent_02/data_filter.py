def execute(parameters, context=None):
    """Filter a list of dictionaries based on a condition string."""
    try:
        data = parameters.get('data')
        condition = parameters.get('condition')
        if not isinstance(data, list) or not isinstance(condition, str):
            return {"error": "Invalid input types."}
        filtered = []
        for item in data:
            try:
                if eval(condition, {}, item):
                    filtered.append(item)
            except Exception:
                continue
        return {"result": filtered}
    except Exception as e:
        return {"error": str(e)}