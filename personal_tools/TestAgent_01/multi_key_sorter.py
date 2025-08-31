def execute(parameters, context=None):
    """Sorts a list of dicts or tuples based on multiple keys with specified order."""
    try:
        data = parameters.get('data')
        sort_keys = parameters.get('sort_keys', [])
        orders = parameters.get('orders', [])
        key_funcs = parameters.get('key_funcs', [None] * len(sort_keys))
        
        if not isinstance(data, list):
            raise ValueError("Data must be a list.")
        if len(sort_keys) != len(orders):
            raise ValueError("sort_keys and orders must have the same length.")
        if len(key_funcs) != len(sort_keys):
            key_funcs = [None] * len(sort_keys)
        
        def composite_key(item):
            keys = []
            for i, key in enumerate(sort_keys):
                func = key_funcs[i]
                if func:
                    k = func(item)
                elif isinstance(item, dict):
                    k = item.get(key)
                elif isinstance(item, tuple) and isinstance(key, int):
                    k = item[key]
                else:
                    k = getattr(item, key, None)
                keys.append(k)
            return tuple(keys)
        
        sorted_data = sorted(data, key=composite_key)
        # Apply order reversal for descending keys
        for i, order in enumerate(orders):
            if order == 'desc':
                sorted_data = sorted(sorted_data, key=lambda x: composite_key(x)[i], reverse=True)
        return {"result": sorted_data}
    except Exception as e:
        return {"error": str(e)}