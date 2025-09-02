import sys
import os
import json
from datetime import datetime

def run_tests():
    results = {
        "tool_name": "MultiCriteriaOrder",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the MultiCriteriaOrder module
    try:
        sys.path.append(os.path.dirname(__file__))
        import MultiCriteriaOrder
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record_result(test_name, passed, error_msg=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error_msg
        })

    # 1. Normal usage: multiple keys with different directions
    try:
        data1 = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30}
        ]
        criteria1 = [("age", "asc"), ("name", "desc")]
        expected1 = [
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30},
            {"name": "Alice", "age": 30}
        ]
        result1 = MultiCriteriaOrder.MultiCriteriaOrder(data=data1, criteria=criteria1)
        if result1 == expected1:
            record_result("Normal usage with multiple keys", True)
        else:
            record_result("Normal usage with multiple keys", False, f"Expected {expected1}, got {result1}")
    except Exception as e:
        record_result("Normal usage with multiple keys", False, str(e))
    
    # 2. Edge case: empty dataset
    try:
        data2 = []
        criteria2 = [("anykey", "asc")]
        expected2 = []
        result2 = MultiCriteriaOrder.MultiCriteriaOrder(data=data2, criteria=criteria2)
        if result2 == expected2:
            record_result("Empty dataset", True)
        else:
            record_result("Empty dataset", False, f"Expected {expected2}, got {result2}")
    except Exception as e:
        record_result("Empty dataset", False, str(e))
    
    # 3. Edge case: dataset with missing keys
    try:
        data3 = [
            {"name": "Alice"},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30}
        ]
        criteria3 = [("age", "asc")]
        # Items missing 'age' should be sorted as if 'age' is None or treated as less
        result3 = MultiCriteriaOrder.MultiCriteriaOrder(data=data3, criteria=criteria3)
        # Expect items with missing 'age' to come first or last depending on implementation
        # Since implementation isn't specified, assume missing keys are treated as None
        expected3 = [
            {"name": "Alice"},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30}
        ]
        if result3 == expected3:
            record_result("Dataset with missing keys", True)
        else:
            record_result("Dataset with missing keys", False, f"Expected {expected3}, got {result3}")
    except Exception as e:
        record_result("Dataset with missing keys", False, str(e))
    
    # 4. Error condition: invalid criteria direction