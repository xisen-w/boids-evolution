import pandas as pd
from datetime import datetime
import sys
import os

def run_tests():
    results = {
        "tool_name": "sort_data",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Import the sort_data module
    try:
        sys.path.append(os.path.dirname(__file__))
        import sort_data
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record_result(test_name, passed, message=""):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "message": message
        })

    # 1. Normal usage: sort by a single column ascending
    df1 = pd.DataFrame({
        'A': [3, 1, 2],
        'B': ['x', 'y', 'z']
    })
    try:
        sorted_df = sort_data.sort_data(df1, ['A'])
        expected = pd.DataFrame({'A': [1, 2, 3], 'B': ['y', 'z', 'x']}).reset_index(drop=True)
        if sorted_df.reset_index(drop=True).equals(expected):
            record_result("Normal usage - single column ascending", True)
        else:
            record_result("Normal usage - single column ascending", False, "DataFrame not sorted as expected.")
    except Exception as e:
        record_result("Normal usage - single column ascending", False, str(e))
    
    # 2. Normal usage: sort by multiple columns with different orders
    df2 = pd.DataFrame({
        'A': [2, 1, 2, 1],
        'B': ['b', 'a', 'a', 'b']
    })
    try:
        sorted_df2 = sort_data.sort_data(df2, ['A', 'B'], [True, False])
        expected2 = pd.DataFrame({
            'A': [1, 1, 2, 2],
            'B': ['b', 'a', 'a', 'b']
        }).reset_index(drop=True)
        if sorted_df2.reset_index(drop=True).equals(expected2):
            record_result("Multi-column sort with different orders", True)
        else:
            record_result("Multi-column sort with different orders", False, "DataFrame not sorted as expected.")
    except Exception as e:
        record_result("Multi-column sort with different orders", False, str(e))
    
    # 3. Edge case: empty DataFrame
    df_empty = pd.DataFrame(columns=['A', 'B'])
    try:
        sorted_empty = sort_data.sort_data(df_empty, ['A'])
        if sorted_empty.equals(df_empty):
            record_result("Empty DataFrame", True)
        else:
            record_result("Empty DataFrame", False, "Sorted empty DataFrame differs from original.")
    except Exception as e:
        record_result("Empty DataFrame", False, str(e))
    
    # 4. Error condition: column does not exist
    df3 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    try:
        sort_data.sort_data(df3, ['C'])
        record_result("Invalid column name", False, "Expected error not raised.")
    except KeyError:
        record_result("Invalid column name", True)
    except Exception as e:
        record_result("Invalid column name", False, f"Unexpected error: {str(e)}