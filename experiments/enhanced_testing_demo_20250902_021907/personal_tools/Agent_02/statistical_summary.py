def execute(parameters, context=None):
    """Compute basic statistical metrics: mean, median, variance, and standard deviation."""
    import math

    data = parameters.get('data')
    if not isinstance(data, list):
        return {"error": "Input data must be a list."}
    if len(data) == 0:
        return {"error": "Input data list is empty."}
    try:
        numeric_data = [float(x) for x in data]
    except (ValueError, TypeError):
        return {"error": "All data points must be numeric."}

    n = len(numeric_data)
    mean = sum(numeric_data) / n

    sorted_data = sorted(numeric_data)
    mid = n // 2
    if n % 2 == 0:
        median = (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        median = sorted_data[mid]

    variance = sum((x - mean) ** 2 for x in numeric_data) / n
    std_dev = math.sqrt(variance)

    return {
        "mean": mean,
        "median": median,
        "variance": variance,
        "standard_deviation": std_dev
    }