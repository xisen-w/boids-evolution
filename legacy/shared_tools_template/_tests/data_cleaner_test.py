import sys
import os
import json
from datetime import datetime
import pandas as pd


def run_tests():
    results = {
        "tool_name": "data_cleaner",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False,
    }

    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import data_cleaner
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record(name, passed, detail=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        entry = {"name": name, "passed": bool(passed)}
        if detail is not None:
            entry["detail"] = detail
        results["tests"].append(entry)

    df = pd.DataFrame({
        "x": [1, None, 3],
        "y": [None, 5, 6],
        "z": ["a", None, "c"],
    })

    # dropna
    try:
        cleaned = data_cleaner.execute(df, dropna=True)
        passed = (cleaned.shape[0] == 1) and (cleaned.isna().sum().sum() == 0)
        record("dropna_rows", bool(passed))
    except Exception as e:
        record("dropna_rows", False, str(e))

    # fillna scalar
    try:
        cleaned = data_cleaner.execute(df, fillna_value=0)
        passed = (cleaned.isna().sum().sum() == 0) and (cleaned.loc[0, "y"] == 0)
        record("fillna_scalar", bool(passed))
    except Exception as e:
        record("fillna_scalar", False, str(e))

    # fillna map
    try:
        cleaned = data_cleaner.execute(df, fillna_map={"z": "missing"})
        passed = (cleaned["z"].isna().sum() == 0) and (cleaned.loc[1, "z"] == "missing")
        record("fillna_map", bool(passed))
    except Exception as e:
        record("fillna_map", False, str(e))

    results["all_passed"] = results["failed_tests"] == 0
    return results


if __name__ == "__main__":
    print(json.dumps(run_tests(), indent=2))
