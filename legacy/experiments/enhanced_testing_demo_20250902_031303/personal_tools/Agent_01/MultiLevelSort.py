def execute(parameters, context=None):
    """MultiLevelSort: Hierarchical multi-criteria sorting of datasets."""
    try:
        data = parameters.get('data')
        criteria = parameters.get('criteria', [])
        if not isinstance(data, list) or not isinstance(criteria, list):
            return {"error": "Invalid input types."}
        def get_key(item, key_path):
            parts = key_path.split('.')
            for part in parts:
                if isinstance(item, dict):
                    item = item.get(part, None)
                elif isinstance(item, list):
                    try:
                        index = int(part)
                        item = item[index]
                    except:
                        return None
                else:
                    return None
            return item
        def sort_key(item):
            key_list = []
            for c in criteria:
                val = get_key(item, c['key'])
                key_list.append(val)
            return tuple(key_list)
        for c in reversed(criteria):
            reverse = c.get('order', 'asc') == 'desc'
            data = sorted(data, key=lambda x: get_key(x, c['key']), reverse=reverse)
        return {"result": data}
    except Exception as e:
        return {"error": str(e)}