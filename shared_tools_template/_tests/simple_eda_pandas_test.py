import sys
import os
import json
from datetime import datetime

import pandas as pd

def run_tests():
    """Basic tests for the simple pandas EDA tool."""
    results = {
        "tool_name": "simple_eda_pandas",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }

    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import simple_eda_pandas
    except Exception as exc:
        results["import_error"] = str(exc)
        return results

    df = pd.DataFrame(
        {
            "species": ["a", "b", "a", None],
            "length": [1.0, 2.5, None, 3.2],
            "weight": [10, 20, 15, None],
        }
    )

    results["total_tests"] += 1
    try:
        summary = simple_eda_pandas.execute(df, target_column="species")
        passed = (
            summary["shape"] == df.shape
            and set(summary["columns"]) == set(df.columns)
            and "target_stats" in summary
        )
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({"name": "basic_summary", "passed": passed})
    except Exception as exc:
        results["failed_tests"] += 1
        results["tests"].append({"name": "basic_summary", "passed": False, "error": str(exc)})

    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    print(json.dumps(run_tests(), indent=2))
