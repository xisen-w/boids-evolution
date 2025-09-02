def execute(parameters, context=None):
    """Normalize numerical data to a specified range, handling missing values."""
    try:
        data = parameters.get('data')
        target_min = parameters.get('target_min', 0)
        target_max = parameters.get('target_max', 1)
        fill_method = parameters.get('fill_method', None)  # e.g., 'mean', 'zero', or None

        if data is None:
            raise ValueError("Data parameter is required.")

        # Convert data to list if it's not already
        data_list = list(data)

        # Handle missing values
        if fill_method == 'mean':
            valid_values = [x for x in data_list if x is not None]
            mean_value = sum(valid_values) / len(valid_values) if valid_values else 0
            data_filled = [x if x is not None else mean_value for x in data_list]
        elif fill_method == 'zero':
            data_filled = [x if x is not None else 0 for x in data_list]
        else:
            data_filled = [x for x in data_list if x is not None]
            if len(data_filled) != len(data_list):
                raise ValueError("Missing values found. Set fill_method to handle them.")

        data_min = min(data_filled)
        data_max = max(data_filled)

        if data_max == data_min:
            normalized = [target_min for _ in data_filled]
        else:
            normalized = [((x - data_min) / (data_max - data_min)) * (target_max - target_min) + target_min for x in data_filled]

        return {"result": normalized}
    except Exception as e:
        return {"error": str(e)}