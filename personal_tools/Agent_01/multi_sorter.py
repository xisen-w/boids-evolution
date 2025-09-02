def execute(parameters, context=None):
    """A versatile sorting utility supporting quicksort, mergesort, and bubblesort."""
    def quicksort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quicksort(left) + middle + quicksort(right)

    def mergesort(arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = mergesort(arr[:mid])
        right = mergesort(arr[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def bubblesort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    data = parameters.get('data')
    algorithm = parameters.get('algorithm', '').lower()

    if not isinstance(data, list):
        return {"error": "Invalid data: expected a list."}
    if algorithm not in ('quicksort', 'mergesort', 'bubblesort'):
        return {"error": "Invalid algorithm. Choose 'quicksort', 'mergesort', or 'bubblesort'."}

    try:
        if algorithm == 'quicksort':
            sorted_data = quicksort(data)
        elif algorithm == 'mergesort':
            sorted_data = mergesort(data)
        else:
            sorted_data = bubblesort(data.copy())
        return {"sorted": sorted_data}
    except Exception as e:
        return {"error": str(e)}