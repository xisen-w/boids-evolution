def execute(parameters, context=None):
    import pandas as pd
    try:
        data = parameters.get('data')
        operation = parameters.get('operation')
        df = pd.read_json(data) if isinstance(data, str) else pd.DataFrame(data)
        if operation == 'pivot':
            index = parameters.get('index')
            columns = parameters.get('columns')
            values = parameters.get('values')
            df = df.pivot(index=index, columns=columns, values=values)
        elif operation == 'melt':
            id_vars = parameters.get('id_vars')
            var_name = parameters.get('var_name', 'variable')
            value_name = parameters.get('value_name', 'value')
            df = pd.melt(df, id_vars=id_vars, var_name=var_name, value_name=value_name)
        elif operation == 'merge':
            other_data = parameters.get('other_data')
            how = parameters.get('how', 'inner')
            on = parameters.get('on')
            other_df = pd.read_json(other_data) if isinstance(other_data, str) else pd.DataFrame(other_data)
            df = pd.merge(df, other_df, how=how, on=on)
        elif operation == 'split':
            column = parameters.get('column')
            value = parameters.get('value')
            df = df[df[column] == value]
        elif operation == 'transpose':
            df = df.transpose()
        result = df.to_json()
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}