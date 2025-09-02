def execute(parameters, context=None):
    """Adaptive sorter supporting multiple algorithms and multi-criteria sorting."""
    try:
        data = parameters.get('dataset')
        algorithm = parameters.get('algorithm', 'quicksort')
        compare_fn = parameters.get('compare_fn')
        criteria = parameters.get('criteria', [])
        if data is None or not isinstance(data, list):
            return {"error": "Invalid or missing dataset."}
        def default_compare(a, b):
            return (a > b) - (a < b)
        def multi_key(item):
            return tuple(item[attr] if order == 'asc' else -item[attr] for attr, order in criteria)
        def cmp(a, b):
            for attr, order in criteria:
                a_val = a.get(attr) if isinstance(a, dict) else getattr(a, attr, None)
                b_val = b.get(attr) if isinstance(b, dict) else getattr(b, attr, None)
                res = (a_val > b_val) - (a_val < b_val) if compare_fn is None else compare_fn(a_val, b_val)
                if res != 0:
                    return res if order == 'asc' else -res
            return 0
        def sort_key(item):
            return tuple(item[attr] if order == 'asc' else -item[attr] for attr, order in criteria)
        if compare_fn:
            key_func = None
        elif criteria:
            key_func = sort_key
        else:
            key_func = None
        if algorithm == 'quicksort':
            sorted_data = sorted(data, key=key_func)
        elif algorithm == 'mergesort':
            sorted_data = sorted(data, key=key_func)
        elif algorithm == 'heapsort':
            import heapq
            heapq.heapify(data)
            sorted_data = [heapq.heappop(data) for _ in range(len(data))]
        else:
            return {"error": "Unknown algorithm."}
        return {"sorted": sorted_data}
    except Exception as e:
        return {"error": str(e)}