def execute(parameters, context=None):
    """MultiKeySort: Sorts a list of dicts or objects by multiple keys with specified order."""
    try:
        data = parameters.get('data')
        keys = parameters.get('keys', [])
        orders = parameters.get('orders', [])
        comparator = parameters.get('comparator', None)

        if not isinstance(data, list):
            raise ValueError("Data should be a list.")
        if len(keys) != len(orders):
            raise ValueError("Keys and orders must be of the same length.")

        # Prepare list of (key, reverse) tuples
        key_orders = list(zip(keys, orders))
        # Build a list of functions to extract each key's value
        def get_value(item, key):
            if isinstance(item, dict):
                return item.get(key)
            else:
                return getattr(item, key, None)

        # Create a composite key function
        def sort_key(item):
            key_values = []
            for key, order in key_orders:
                val = get_value(item, key)
                # For descending, invert the value if possible
                if order == 'desc':
                    # For numbers or strings, invert by wrapping in a tuple
                    # or use a trick; here, we invert for numbers
                    if isinstance(val, (int, float)):
                        val = -val
                    elif isinstance(val, str):
                        val = ''.join(chr(255 - ord(c)) for c in val)
                    # For other types, leave as is
                key_values.append(val)
            return tuple(key_values)

        # Sort data with custom key
        sorted_data = sorted(data, key=sort_key)
        return {"result": sorted_data}
    except Exception as e:
        return {"error": str(e)}