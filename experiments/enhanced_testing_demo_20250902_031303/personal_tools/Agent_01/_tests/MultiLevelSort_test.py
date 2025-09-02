import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for MultiLevelSort"""
    results = {
        "tool_name": "MultiLevelSort",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    
    # Attempt to import the MultiLevelSort module
    try:
        # Assuming MultiLevelSort is available as a module named 'MultiLevelSort'
        import MultiLevelSort
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

    # Test 1: Normal usage with flat dictionaries
    try:
        data1 = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        criteria1 = [{'key': 'age', 'order': 'asc'}]
        sorted1 = MultiLevelSort(data=data1, criteria=criteria1)
        expected1 = [
            {'name': 'Bob', 'age': 25},
            {'name': 'Alice', 'age': 30},
            {'name': 'Charlie', 'age': 35}
        ]
        passed = sorted1 == expected1
        record_result("Normal usage flat dicts", passed)
    except Exception as e:
        record_result("Normal usage flat dicts", False, str(e))
    
    # Test 2: Multi-criteria sorting with nested keys
    try:
        data2 = [
            {'name': 'Alice', 'score': 90, 'address': {'city': 'NY'}},
            {'name': 'Bob', 'score': 85, 'address': {'city': 'LA'}},
            {'name': 'Charlie', 'score': 90, 'address': {'city': 'LA'}},
            {'name': 'David', 'score': 85, 'address': {'city': 'NY'}}
        ]
        criteria2 = [
            {'key': 'score', 'order': 'desc'},
            {'key': 'address.city', 'order': 'asc'}
        ]
        sorted2 = MultiLevelSort(data=data2, criteria=criteria2)
        expected2 = [
            {'name': 'Charlie', 'score': 90, 'address': {'city': 'LA'}},
            {'name': 'Alice', 'score': 90, 'address': {'city': 'NY'}},
            {'name': 'David', 'score': 85, 'address': {'city': 'NY'}},
            {'name': 'Bob', 'score': 85, 'address': {'city': 'LA'}}
        ]
        passed = sorted2 == expected2
        record_result("Multi-criteria nested keys", passed)
    except Exception as e:
        record_result("Multi-criteria nested keys", False, str(e))
    
    # Test 3: Handling missing keys gracefully
    try:
        data3 = [
            {'name': 'Eve', 'score': 88},
            {'name': 'Frank'},  # missing 'score'
            {'name': 'Grace', 'score': 92}
        ]
        criteria3 = [{'key': 'score', '