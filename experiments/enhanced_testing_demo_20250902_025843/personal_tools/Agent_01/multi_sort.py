def execute(parameters, context=None):
    """Sorts a list using specified algorithm ('quick' or 'merge')."""
    try:
        data_list = parameters.get('data_list')
        algorithm = parameters.get('algorithm', 'quick').lower()
        if not isinstance(data_list, list):
            return {"error": "data_list must be a list."}
        if algorithm not in ('quick', 'merge'):
            return {"error": "Unsupported algorithm. Choose 'quick' or 'merge'."}
        
        def quicksort(lst):
            if len(lst) <= 1:
                return lst
            pivot = lst[len(lst) // 2]
            left = [x for x in lst if x < pivot]
            middle = [x for x in lst if x == pivot]
            right = [x for x in lst if x > pivot]
            return quicksort(left) + middle + quicksort(right)
        
        def mergesort(lst):
            if len(lst) <= 1:
                return lst
            mid = len(lst) // 2
            left = mergesort(lst[:mid])
            right = mergesort(lst[mid:])
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
        
        if algorithm == 'quick':
            sorted_list = quicksort(data_list)
        else:
            sorted_list = mergesort(data_list)
        return {"sorted": sorted_list}
    except Exception as e:
        return {"error": str(e)}