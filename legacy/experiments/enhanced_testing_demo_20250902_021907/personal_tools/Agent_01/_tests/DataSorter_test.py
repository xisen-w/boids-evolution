import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for DataSorter"""
    results = {
        "tool_name": "DataSorter",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the DataSorter module
    try:
        sys.path.append(os.path.dirname(__file__))
        import DataSorter
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

    # 1. Normal usage: sort list of dicts by a single key ascending
    try:
        data = [{'name': 'A', 'value': 10}, {'name': 'B', 'value': 5}]
        sorted_data = DataSorter.execute(data=data, sort_keys='value', ascending=True)
        expected = [{'name': 'B', 'value': 5}, {'name': 'A', 'value': 10}]
        passed = sorted_data == expected
        record_result("Sort list of dicts by 'value' ascending", passed)
    except Exception as e:
        record_result("Sort list of dicts by 'value' ascending", False, str(e))
    
    # 2. Normal usage: sort list of dicts by multiple keys descending
    try:
        data = [
            {'name': 'A', 'value': 10},
            {'name': 'B', 'value': 10},
            {'name': 'C', 'value': 5}
        ]
        sorted_data = DataSorter.execute(data=data, sort_keys=['value', 'name'], ascending=False)
        expected = [
            {'name': 'B', 'value': 10},
            {'name': 'A', 'value': 10},
            {'name': 'C', 'value': 5}
        ]
        passed = sorted_data == expected
        record_result("Sort list of dicts by multiple keys descending", passed)
    except Exception as e:
        record_result("Sort list of dicts by multiple keys descending", False, str(e))
    
    # 3. Edge case: empty list input
    try:
        data = []
        sorted_data = DataSorter.execute(data=data)
        passed = sorted_data == []
        record_result("Sort empty list", passed)
    except Exception as e:
        record_result("Sort empty list", False, str(e))
    
    # 4. Error condition: invalid data type (integer)
    try:
        data = 12345
        DataSorter.execute(data=data)
        record_result("Invalid data type (int)", False, "Expected exception not raised")
    except Exception:
        record_result("Invalid data type (int)", True)
    
    # 5. Parameter validation: invalid sort_keys type
    try:
        data = [{'a': 1}]
        DataSorter.execute(data=data, sort_keys=123)
        record_result("Invalid sort_keys type (int)", False, "Expected exception not raised")
    except Exception:
        record_result("Invalid sort_keys type (int)", True)
    
    # 6. Sorting DataFrame-like structure (simulate with list of dicts)
    try:
        data = [
            {'name': 'X', 'score': 90},
            {'name': 'Y', 'score':