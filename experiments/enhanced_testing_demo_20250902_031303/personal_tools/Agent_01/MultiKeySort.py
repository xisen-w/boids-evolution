def execute(parameters, context=None):
    """MultiKeySort: Sorts data by multiple keys with optional custom comparators."""
    try:
        data = parameters.get('data')
        sort_keys = parameters.get('sort_keys', [])
        data_types = parameters.get('data_types', {})

        def get_key_func(key_info):
            key_name = key_info['key']
            order = key_info.get('order', 'asc')
            comparator = key_info.get('comparator')

            def key_func(item):
                val = item[key_name] if isinstance(item, dict) else item[key_name]
                dtype = data_types.get(key_name)
                if comparator:
                    return comparator(val)
                if dtype == 'numeric':
                    return float(val)
                elif dtype == 'date':
                    return val  # assume date objects or parse if needed
                else:
                    return val
            return key_func, order

        key_funcs_orders = [get_key_func(k) for k in sort_keys]
        def sort_key(item):
            keys = []
            for func, order in key_funcs_orders:
                val = func(item)
                keys.append(val if order == 'asc' else (float('inf') if isinstance(val, (int, float)) else val))
            return tuple(keys)

        reverse_flags = [k.get('order', 'asc') == 'desc' for k in sort_keys]
        # Since Python's sorted doesn't support multiple reverse flags, we sort iteratively
        for i in reversed(range(len(sort_keys))):
            key_func, order = key_funcs_orders[i]
            data = sorted(data, key=key_func, reverse=(order=='desc'))
        return {"result": data}
    except Exception as e:
        return {"error": str(e)}