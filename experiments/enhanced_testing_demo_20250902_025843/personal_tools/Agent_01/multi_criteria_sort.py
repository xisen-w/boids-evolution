def execute(parameters, context=None):
    """Multi-Criteria Sorting Engine"""
    try:
        data = parameters.get('data')
        criteria = parameters.get('criteria', [])
        stability = parameters.get('stability', True)

        if not isinstance(data, list):
            return {"error": "Invalid data: expected a list."}
        if not isinstance(criteria, list):
            return {"error": "Invalid criteria: expected a list."}

        def build_key(item):
            key_list = []
            for crit in criteria:
                key_name = crit.get('key')
                nulls_first = crit.get('nulls_first', False)
                value = item.get(key_name) if isinstance(item, dict) else getattr(item, key_name, None)
                # Handle nulls
                if value is None:
                    null_flag = 0 if nulls_first else 1
                    key_list.append((null_flag, None))
                else:
                    key_list.append((1, value))
            return tuple(key_list)

        # Determine overall reverse flags for sorting
        reverses = [crit.get('reverse', False) for crit in criteria]

        # Perform multi-criteria sort
        sorted_data = sorted(
            data,
            key=build_key,
            reverse=any(reverses) if len(reverses) == 1 else False
        )

        # For multiple criteria, perform stable sorts in reverse order
        for index in reversed(range(len(criteria))):
            key_name = criteria[index].get('key')
            reverse = criteria[index].get('reverse', False)
            nulls_first = criteria[index].get('nulls_first', False)
            def sort_key(item):
                val = item.get(key_name) if isinstance(item, dict) else getattr(item, key_name, None)
                if val is None:
                    return 0 if nulls_first else 1
                return 1, val
            sorted_data = sorted(
                sorted_data,
                key=sort_key,
                reverse=reverse
            )

        return {"result": sorted_data}
    except Exception as e:
        return {"error": str(e)}