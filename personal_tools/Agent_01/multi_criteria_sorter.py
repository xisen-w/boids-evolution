def execute(parameters, context=None):
    """Multi-criteria sorter: sorts data based on multiple keys with priorities and order."""
    try:
        data = parameters.get('data')
        sort_keys = parameters.get('sort_keys', [])
        orders = parameters.get('orders', [])
        priorities = parameters.get('priorities', [])
        
        if not isinstance(data, list):
            raise ValueError("Data should be a list.")
        if not all(callable(k) or isinstance(k, str) for k in sort_keys):
            raise ValueError("sort_keys must be list of callables or attribute names.")
        if orders and len(orders) != len(sort_keys):
            raise ValueError("Length of orders must match sort_keys.")
        if priorities and len(priorities) != len(sort_keys):
            raise ValueError("Length of priorities must match sort_keys.")
        if not priorities:
            priorities = list(range(len(sort_keys)))
        
        # Pair each key with its order and priority
        key_info = list(zip(sort_keys, orders or [True]*len(sort_keys)), priorities)
        # Sort key info by priority
        key_info_sorted = sorted(key_info, key=lambda x: x[1])
        
        def get_sort_value(item, key):
            if callable(key):
                return key(item)
            elif isinstance(item, dict):
                return item.get(key)
            else:
                return getattr(item, key, None)
        
        def composite_key(item):
            key_values = []
            for key, (order, _) in zip([k for k, _ in key_info_sorted], key_info_sorted):
                val = get_sort_value(item, key)
                # For descending order, invert the value if possible
                if order is False:
                    # For numbers and strings, invert by reversing sort order
                    # but since sorted() handles order, we just set key accordingly
                    key_values.append(val)
                else:
                    key_values.append(val)
            return tuple(
                (val if order else _invert(val))
                for (val, (_, order)) in zip(
                    [get_sort_value(item, k) for k in [k for k, _ in key_info_sorted]],
                    key_info_sorted
                )
            )
        
        def _invert(val):
            # For numeric types, invert by negation
            if isinstance(val, (int, float)):
                return -val
            # For strings, invert by reversing string (