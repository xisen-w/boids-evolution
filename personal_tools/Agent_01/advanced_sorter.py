def execute(parameters, context=None):
    """Flexible sorting utility supporting multiple algorithms and options."""
    try:
        data = parameters.get('data')
        method = parameters.get('method', 'quicksort')
        criteria = parameters.get('criteria', None)
        optimize = parameters.get('optimize', 'speed')
        descending = parameters.get('descending', False)
        large_dataset = parameters.get('large_dataset', False)

        if data is None:
            raise ValueError("Data parameter is required.")

        def quicksort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr)//2]
            left = [x for x in arr if (criteria(x) if criteria else x) < (criteria(pivot) if criteria else pivot)]
            middle = [x for x in arr if (criteria(x) if criteria else x) == (criteria(pivot) if criteria else pivot)]
            right = [x for x in arr if (criteria(x) if criteria else x) > (criteria(pivot) if criteria else pivot)]
            return quicksort(left) + middle + quicksort(right)

        def mergesort(arr):
            if len(arr) <= 1:
                return arr
            mid = len(arr)//2
            left = mergesort(arr[:mid])
            right = mergesort(arr[mid:])
            result = []
            i = j = 0
            while i < len(left) and j < len(right):
                left_key = criteria(left[i]) if criteria else left[i]
                right_key = criteria(right[j]) if criteria else right[j]
                if left_key <= right_key:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            result.extend(left[i:])
            result.extend(right[j:])
            return result

        def heapsort(arr):
            import heapq
            heap = [(criteria(x) if criteria else x, x) for x in arr]
            heapq.heapify(heap)
            sorted_list = [heapq.heappop(heap)[1] for _ in range(len(heap))]
            return sorted_list

        # Select algorithm
        if method == 'quicksort':
            sorted_data = quicksort(data) if optimize == 'speed' else sorted(data, key=criteria, reverse=descending)
        elif method == 'mergesort':
            sorted_data = mergesort(data