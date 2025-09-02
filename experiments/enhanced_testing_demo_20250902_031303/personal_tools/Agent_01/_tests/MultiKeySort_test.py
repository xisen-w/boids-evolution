import sys
import os
import json
from datetime import datetime
from functools import cmp_to_key

def run_tests():
    results = {
        "tool_name": "MultiKeySort",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    try:
        import MultiKeySort
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

    # Helper comparator functions
    def numeric_comparator(a, b):
        return (a > b) - (a < b)

    def date_comparator(a, b):
        return (a > b) - (a < b)

    # Test 1: Normal usage with list of dicts, multi-level sorting
    try:
        dataset = [
            {'name': 'Alice', 'score': 90, 'date': '2023-01-10'},
            {'name': 'Bob', 'score': 85, 'date': '2023-01-12'},
            {'name': 'Charlie', 'score': 90, 'date': '2023-01-11'},
            {'name': 'David', 'score': 85, 'date': '2023-01-10'}
        ]
        sorted_data = MultiKeySort(
            data=dataset,
            sort_keys=[
                {'key': 'score', 'order': 'asc'},
                {'key': 'date', 'order': 'desc', 'comparator': date_comparator}
            ],
            data_types={'score': 'numeric', 'date': 'date'}
        )
        expected = [
            {'name': 'David', 'score': 85, 'date': '2023-01-10'},
            {'name': 'Bob', 'score': 85, 'date': '2023-01-12'},
            {'name': 'Charlie', 'score': 90, 'date': '2023-01-11'},
            {'name': 'Alice', 'score': 90, 'date': '2023-01-10'}
        ]
        passed = sorted_data == expected
        record_result("Normal usage multi-level sort", passed, "" if passed else f"Expected {expected}, got {sorted_data}")
    except Exception as e:
        record_result("Normal usage multi-level sort", False, str(e))

    # Test 2: Edge case with empty dataset
    try:
        empty_data = []
        sorted_empty = MultiKeySort(
            data=empty_data,
            sort_keys=[{'key': 'any'}]
        )
        passed = sorted_empty == []
        record_result("Empty dataset", passed, "" if passed else f"Expected [], got {sorted_empty}")
    except Exception as e:
        record_result("Empty dataset", False, str(e))

    # Test 3: Dataset with mixed data types and explicit data_types
    try:
        dataset = [
            ['2023-01-10', 100],
            ['2023-01-12', 50],
            ['2023-01-11', 75]
        ]
        sorted_data = MultiKeySort(
            data=dataset,
            sort_keys=[
                {'key': 0, 'order': 'asc', 'comparator': date_comparator},