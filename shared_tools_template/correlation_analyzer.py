import pandas as pd
from typing import Union, List, Optional

def execute(
    data: Union[str, pd.DataFrame],
    columns: Optional[List[str]] = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Calculate correlation matrix for numeric columns in a dataset.
    
    Args:
        data: CSV file path or pandas DataFrame
        columns: List of column names to analyze (None = all numeric columns)
        method: Correlation method ('pearson', 'kendall', 'spearman')
    
    Returns:
        Correlation matrix as pandas DataFrame
    """
    # Load data if it's a file path
    df = pd.read_csv(data) if isinstance(data, str) else data.copy()
    
    # Select columns to analyze
    if columns is None:
        # Use all numeric columns
        cols = df.select_dtypes(include="number").columns
    else:
        # Filter to requested columns that exist and are numeric
        cols = [c for c in columns if c in df.columns and df[c].dtype in ['int64', 'float64']]
    
    # Calculate correlation matrix
    return df.loc[:, cols].corr(method=method)
