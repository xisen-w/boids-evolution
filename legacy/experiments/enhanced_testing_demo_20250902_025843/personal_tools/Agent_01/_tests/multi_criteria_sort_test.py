import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for multi_criteria_sort"""
    results = {
        "tool_name": "multi_criteria_sort",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    
    # Attempt to import the multi_criteria_sort module
    try:
        sys.path.append(os.path.dirname(__file__))
        import multi_criteria_sort
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record_result(test_name, passed, error_msg=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
            results["all_passed"] = False
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error_msg
        })

    # Test 1: Normal usage with dictionaries, multiple criteria
    try:
        data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': None},
            {'name': 'Charlie', 'age': 25},
            {'name': 'Alice', 'age': 22}
        ]
        criteria = [
            {'key': 'name', 'reverse': False, 'nulls_first': True},
            {'key': 'age', 'reverse': False, 'nulls_first': False}
        ]
        expected = [
            {'name': 'Alice', 'age': 22},
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': None},
            {'name': 'Charlie', 'age': 25}
        ]
        result = multi_criteria_sort.multi_criteria_sort(data, criteria, stability=True)
        passed = result == expected
        record_result("Normal usage with dictionaries", passed)
        if not passed:
            record_result("Normal usage with dictionaries - mismatch", False, f"Expected: {expected}, Got: {result}")
    except Exception as e:
        record_result("Normal usage with dictionaries", False, str(e))
    
    # Test 2: Edge case with empty data list
    try:
        data = []
        criteria = [{'key': 'name', 'reverse': False, 'nulls_first': True}]
        result = multi_criteria_sort.multi_criteria_sort(data, criteria)
        passed = result == []
        record_result("Empty data list", passed)
        if not passed:
            record_result("Empty data list - mismatch", False, f"Expected: [], Got: {result}")
    except Exception as e:
        record_result("Empty data list", False, str(e))
    
    # Test 3: Data with all nulls for sorting key
    try:
        data = [
            {'name': None, 'score': 10},
            {'name': None, 'score': 20}
        ]
        criteria = [{'key': 'name', 'reverse': False, 'nulls_first': True}]
        result = multi_criteria_sort.multi_criteria_sort(data, criteria)
        # Expect original order preserved due to stability
        expected = data
        passed = result == expected
        record_result("All nulls for key", passed)
        if not passed:
            record_result("All nulls for key - mismatch", False, f"Expected: {expected}, Got: {result}")
    except Exception as e:
        record_result("All nulls for key", False, str(e))
    
    # Test 4: Invalid criteria parameter (not a