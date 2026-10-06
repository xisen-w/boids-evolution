def execute(parameters, context=None):
    """Sorts a list of dicts or tuples based on specified keys and options."""
    try:
        data = parameters.get('data')
        keys = parameters.get('keys', [])
        orders = parameters.get('orders', [True] * len(keys))
        algorithm = parameters.get('algorithm', 'quicksort')
        stable = parameters.get('stable', False)

        if not isinstance(data, list) or not all(isinstance(item, (dict, tuple)) for item in data):
            return {"error": "Invalid data format"}

        def get_key(item):
            return tuple(item[k] if isinstance(item, dict) else item[k] for k in keys)

        reverse_flags = [not o for o in orders]

        def sort_func(a, b):
            for idx, key in enumerate(keys):
                a_val = a[key] if isinstance(a, dict) else a[key]
                b_val = b[key] if isinstance(b, dict) else b[key]
                if a_val != b_val:
                    return (a_val > b_val) - (a_val < b_val) if not reverse_flags[idx] else (b_val > a_val) - (b_val < a_val)
            return 0

        def quicksort(lst):
            if len(lst) <= 1:
                return lst
            pivot = lst[len(lst)//2]
            left, right = [], []
            for item in lst:
                cmp = sort_func(item, pivot)
                if cmp < 0:
                    left.append(item)
                elif cmp > 0:
                    right.append(item)
                else:
                    if stable:
                        left.append(item)
                    else:
                        right.append(item)
            return quicksort(left) + quicksort(right)

        def mergesort(lst):
            if len(lst) <= 1:
                return lst
            mid = len(lst)//2
            left = mergesort(lst[:mid])
            right = mergesort(lst[mid:])
            return merge(left, right)

        def merge(left, right):
            result = []
            i = j = 0
            while i < len(left) and j < len(right):
                cmp = sort_func(left[i], right[j])
                if cmp <= 0:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            result.extend(left[i:])