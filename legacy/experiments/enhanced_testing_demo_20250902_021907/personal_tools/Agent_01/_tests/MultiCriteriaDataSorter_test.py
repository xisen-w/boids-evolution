import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for MultiCriteriaDataSorter"""
    results = {
        "tool_name": "MultiCriteriaDataSorter",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the tool module
    try:
        sys.path.append(os.path.dirname(__file__))
        import MultiCriteriaDataSorter
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

    # Test 1: Normal usage with multiple criteria
    try:
        data = [
            {'name': 'Alice', 'age': 30, 'score': 85},
            {'name': 'Bob', 'age': 25, 'score': 90},
            {'name': 'Charlie', 'age': 30, 'score': 80},
            {'name': 'David', 'age': 25, 'score': 85}
        ]
        criteria = [
            {'key': 'age', 'order': 'asc', 'missing': 'last'},
            {'key': 'score', 'order': 'desc'}
        ]
        sorted_data = MultiCriteriaDataSorter.execute(data, criteria)
        expected = [
            {'name': 'Bob', 'age': 25, 'score': 90},
            {'name': 'David', 'age': 25, 'score': 85},
            {'name': 'Alice', 'age': 30, 'score': 85},
            {'name': 'Charlie', 'age': 30, 'score': 80}
        ]
        assert sorted_data == expected
        record_result("Normal usage multiple criteria", True)
    except Exception as e:
        record_result("Normal usage multiple criteria", False, str(e))
    
    # Test 2: Handling missing values with 'missing' parameter
    try:
        data = [
            {'name': 'Eve', 'score': 70},
            {'name': 'Frank', 'score': 75},
            {'name': 'Grace'}  # missing score
        ]
        criteria = [
            {'key': 'score', 'order': 'asc', 'missing': 'first'}
        ]
        sorted_data = MultiCriteriaDataSorter.execute(data, criteria)
        expected = [
            {'name': 'Grace'},
            {'name': 'Eve', 'score': 70},
            {'name': 'Frank', 'score': 75}
        ]
        assert sorted_data == expected
        record_result("Missing values with missing='first'", True)
    except Exception as e:
        record_result("Missing values with missing='first'", False, str(e))
    
    # Test 3: Custom comparator function usage
    try:
        def custom_name_length(a, b):
            return len(a['name']) - len(b['name'])
        data = [
            {'name': 'Ann', 'score': 88},
            {'name': 'Bob', 'score': 92},
            {'name': 'Charlie', 'score': 85}
        ]
        criteria = [
            {'key': 'name', 'order': 'asc', 'comparator': custom_name_length}
        ]
        sorted_data = MultiCriteriaDataSorter.execute(data, criteria)
        expected =