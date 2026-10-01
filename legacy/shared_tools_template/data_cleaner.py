import pandas as pd
from typing import Union, Optional, Dict, Any


def execute(
    data: Union[str, pd.DataFrame],
    dropna: bool = False,
    fillna_value: Optional[Any] = None,
    fillna_map: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Clean datasets by dropping and/or filling missing values.

    - data: CSV path or DataFrame
    - dropna: drop rows with any NA
    - fillna_value: scalar to fill all NA
    - fillna_map: per-column fill mapping
    Returns a new cleaned DataFrame.
    """
    df = pd.read_csv(data) if isinstance(data, str) else data.copy()

    if dropna:
        df = df.dropna()

    if fillna_map is not None:
        df = df.fillna(fillna_map)
    elif fillna_value is not None:
        df = df.fillna(fillna_value)

    return df
