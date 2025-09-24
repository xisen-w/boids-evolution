"""Simple pandas-based exploratory data analysis."""

from typing import Any, Dict, Optional

import pandas as pd


def execute(data: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
    """Return basic dataset diagnostics in a single dictionary."""

    summary: Dict[str, Any] = {
        "shape": data.shape,
        "columns": list(data.columns),
        "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
        "missing": data.isnull().sum().to_dict(),
        "describe": data.describe(include='all').to_dict(),
    }

    if target_column and target_column in data.columns:
        summary["target_stats"] = data[target_column].value_counts(dropna=False).to_dict()

    return summary
