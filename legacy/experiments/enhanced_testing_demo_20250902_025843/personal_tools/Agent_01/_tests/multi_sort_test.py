import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for multi_sort"""
    results = {
        "tool_name": "multi_sort",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    
    # Attempt to import the multi_sort module
    try:
        sys.path.append(os.path.dirname(__file__))
        import multi_sort
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

    # Test 1: Normal usage with quicksort
    try:
        data = [5, 2, 9, 1, 5]
        sorted_data = multi_sort.execute(data, algorithm='quick')
        assert sorted_data == sorted(data)
        record_result("Normal usage with quicksort", True)
    except Exception as e:
        record_result("Normal usage with quicksort", False, str(e))
    
    # Test 2: Normal usage with mergesort
    try:
        data = [3, 7, 2, 8, 1]
        sorted_data = multi_sort.execute(data, algorithm='merge')
        assert sorted_data == sorted(data)
        record_result("Normal usage with mergesort", True)
    except Exception as e:
        record_result("Normal usage with mergesort", False, str(e))
    
    # Test 3: Edge case - empty list
    try:
        data = []
        sorted_data_quick = multi_sort.execute(data, algorithm='quick')
        sorted_data_merge = multi_sort.execute(data, algorithm='merge')
        assert sorted_data_quick == []
        assert sorted_data_merge == []
        record_result("Empty list input", True)
    except Exception as e:
        record_result("Empty list input", False, str(e))
    
    # Test 4: Edge case - list with one element
    try:
        data = [42]
        sorted_quick = multi_sort.execute(data, algorithm='quick')
        sorted_merge = multi_sort.execute(data, algorithm='merge')
        assert sorted_quick == [42]
        assert sorted_merge == [42]
        record_result("Single element list", True)
    except Exception as e:
        record_result("Single element list", False, str(e))
    
    # Test 5: Invalid algorithm parameter
    try:
        data = [1, 2, 3]
        multi_sort.execute(data, algorithm='invalid_algo')
        record_result("Invalid algorithm parameter", False, "Expected exception not raised")
    except ValueError as ve:
        record_result("Invalid algorithm parameter", True)
    except Exception as e:
        record_result("Invalid algorithm parameter", False, str(e))
    
    # Test 6: data_list is not a list
    try:
        data = "not a list"
        multi_sort.execute(data, algorithm='quick')
        record_result("Non-list data_list", False, "Expected exception not raised")
    except TypeError as te:
        record_result("Non-list data_list", True)
    except Exception as e:
        record_result("Non-list data_list", False, str(e))
    
    # Test 7: data_list contains non-comparable items
    try:
        data = [1, 2, '