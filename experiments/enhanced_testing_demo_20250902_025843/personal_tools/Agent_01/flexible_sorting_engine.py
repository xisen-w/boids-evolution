def execute(parameters, context=None):
    """Flexible sorting engine supporting multi-criteria, grouping, and ranking."""
    try:
        data = parameters.get('data')
        sort_keys = parameters.get('sort_keys', [])
        group_by = parameters.get('group_by', None)
        ranking_func = parameters.get('ranking_func', None)

        if not isinstance(data, list):
            raise ValueError("Data must be a list.")

        # Prepare sort parameters
        sort_params = []
        for key, order in sort_keys:
            reverse = (order.lower() == 'desc')
            def key_func(item, k=key):
                return item.get(k, None)
            sort_params.append((key_func, reverse))

        # Apply multi-criteria sorting
        for key_func, reverse in reversed(sort_params):
            data = sorted(data, key=key_func, reverse=reverse)

        # Apply ranking if provided
        if ranking_func:
            data = sorted(data, key=ranking_func, reverse=True)

        # Group data if requested
        if group_by:
            grouped = {}
            for item in data:
                key = item.get(group_by)
                grouped.setdefault(key, []).append(item)
            return {"grouped_data": grouped}

        return {"sorted_data": data}
    except Exception as e:
        return {"error": str(e)}