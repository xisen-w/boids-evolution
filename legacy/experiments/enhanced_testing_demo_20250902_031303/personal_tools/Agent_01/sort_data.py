def execute(parameters, context=None):
    """Sorts a pandas DataFrame based on specified columns and order."""
    import pandas as pd
    try:
        data = parameters.get('data')
        columns = parameters.get('columns')
        ascending = parameters.get('ascending', None)

        if not isinstance(data, pd.DataFrame):
            return {"error": "Parameter 'data' must be a pandas DataFrame."}
        if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
            return {"error": "Parameter 'columns' must be a list of strings."}
        if ascending is not None:
            if not isinstance(ascending, list) or len(ascending) != len(columns):
                return {"error": "Parameter 'ascending' must be a list of booleans with the same length as 'columns'."}
        else:
            ascending = [True] * len(columns)

        for col in columns:
            if col not in data.columns:
                return {"error": f"Column '{col}' does not exist in the DataFrame."}

        sorted_data = data.sort_values(by=columns, ascending=ascending)
        return {"result": sorted_data}
    except Exception as e:
        return {"error": str(e)}