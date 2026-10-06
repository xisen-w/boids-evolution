"""Simple pandas-based exploratory data analysis."""

from typing import Any, Dict, Optional

import pandas as pd


def execute(data, target_column: Optional[str] = None) -> Dict[str, Any]:
    """Return basic dataset diagnostics in a single dictionary."""
    
    # Handle both file paths and DataFrames
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Data must be a file path (str) or pandas DataFrame")

    summary: Dict[str, Any] = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "describe": df.describe(include='all').to_dict(),
    }

    if target_column and target_column in df.columns:
        summary["target_stats"] = df[target_column].value_counts(dropna=False).to_dict()

    return summary
