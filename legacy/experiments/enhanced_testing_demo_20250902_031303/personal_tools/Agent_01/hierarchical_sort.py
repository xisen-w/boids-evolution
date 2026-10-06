def execute(parameters, context=None):
    """Hierarchical sorting of data based on multiple keys and orders."""
    try:
        data = parameters.get('data')
        sort_keys = parameters.get('sort_keys')
        if not isinstance(data, list) or not isinstance(sort_keys, list):
            raise ValueError("Invalid input types.")
        for key, order in reversed(sort_keys):
            reverse = (order == 'desc')
            data.sort(key=lambda x: x[key] if isinstance(x, dict) else x[key], reverse=reverse)
        return {"result": data}
    except Exception as e:
        return {"error": str(e)}