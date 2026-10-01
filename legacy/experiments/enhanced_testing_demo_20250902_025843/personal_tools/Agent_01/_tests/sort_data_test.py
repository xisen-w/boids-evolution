import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for sort_data"""
    results = {
        "tool_name": "sort_data",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    
    # Attempt to import the sort_data module
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
            results["all_passed"] = False
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "message": message
        })

    # Test 1: Normal usage with list of dicts, multi-criteria sorting
    try:
        data = [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": 25, "score": 90},
            {"name": "Charlie", "age": 30, "score": 80},
            {"name": "David", "age": 25, "score": 88}
        ]
        sorted_result = sort_data.execute(
            data=data,
            keys=["age", "score"],
            orders=[True, False],
            algorithm='quicksort',
            stable=True
        )
        expected = [
            {"name": "Bob", "age": 25, "score": 90},
            {"name": "David", "age": 25, "score": 88},
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Charlie", "age": 30, "score": 80}
        ]
        if sorted_result == expected:
            record_result("Normal multi-criteria dicts", True)
        else:
            record_result("Normal multi-criteria dicts", False, f"Expected {expected}, got {sorted_result}")
    except Exception as e:
        record_result("Normal multi-criteria dicts", False, str(e))
    
    # Test 2: Edge case with empty list
    try:
        data = []
        sorted_result = sort_data.execute(
            data=data,
            keys=["any"],
            orders=[True]
        )
        if sorted_result == []:
            record_result("Empty list input", True)
        else:
            record_result("Empty list input", False, f"Expected [], got {sorted_result}")
    except Exception as e:
        record_result("Empty list input", False, str(e))
    
    # Test 3: List of tuples, sorting by index with descending order
    try:
        data = [
            (1, "apple", 3.5),
            (2, "banana", 2.0),
            (3, "cherry", 4.0),
            (2, "date", 3.0)
        ]
        sorted_result = sort_data.execute(
            data=data,
            keys=[0],
            orders=[False],
            algorithm='mergesort'
        )
        expected = [
            (3, "cherry", 4.0),
            (2, "banana", 2.0),
            (2, "date", 3.0),
            (1, "apple", 3.5)
        ]
        if sorted_result == expected:
            record_result("Tuples sorted by