def execute(parameters, context=None):
    """Sorts a list of dictionaries based on multiple keys with specified directions."""
    try:
        data = parameters.get('data')
        criteria = parameters.get('criteria')
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("Invalid data: must be a list of dictionaries.")
        if not isinstance(criteria, list):
            raise ValueError("Invalid criteria: must be a list of (key, direction) tuples.")
        # Prepare sort keys with directions
        def sort_key(item):
            key_values = []
            for key, direction in criteria:
                value = item.get(key)
                key_values.append((value if value is not None else float('-inf')))
            return key_values
        # Determine sort order for each criterion
        directions = [1 if dir.lower() == 'asc' else -1 for _, dir in criteria]
        # Sort data with custom key and directions
        sorted_data = sorted(
            data,
            key=lambda item: [
                (item.get(k) if item.get(k) is not None else float('-inf')) * d
                for (k, _), d in zip(criteria, directions)
            ]
        )
        return {"result": sorted_data}
    except Exception as e:
        return {"error": str(e)}