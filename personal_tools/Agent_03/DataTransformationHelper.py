def execute(parameters, context=None):
    """Data Transformation Helper: filtering, sorting, aggregating, transforming."""
    try:
        data = parameters.get('data')
        action = parameters.get('action')
        result = None

        if action == 'filter':
            condition = parameters.get('condition')
            if not callable(condition):
                return {"error": "Condition must be a callable."}
            result = list(filter(condition, data))
        elif action == 'sort':
            key = parameters.get('key')
            reverse = parameters.get('reverse', False)
            result = sorted(data, key=key, reverse=reverse)
        elif action == 'aggregate':
            group_by = parameters.get('group_by')
            agg_func = parameters.get('agg_func')
            if not callable(agg_func):
                return {"error": "Aggregation function must be callable."}
            grouped = {}
            for item in data:
                key = item.get(group_by)
                grouped.setdefault(key, []).append(item)
            result = {k: agg_func(v) for k, v in grouped.items()}
        elif action == 'transform':
            transform_func = parameters.get('transform_func')
            if not callable(transform_func):
                return {"error": "Transform function must be callable."}
            result = [transform_func(item) for item in data]
        else:
            return {"error": "Invalid action specified."}
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}