import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for hierarchical_sort"""
    results = {
        "tool_name": "hierarchical_sort",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the hierarchical_sort module
    try:
        sys.path.append(os.path.dirname(__file__))
        import hierarchical_sort
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

    # 1. Normal usage: multi-level sorting on list of dicts
    try:
        data1 = [
            {"category": "fruit", "name": "apple", "price": 3},
            {"category": "fruit", "name": "banana", "price": 2},
            {"category": "vegetable", "name": "carrot", "price": 1},
            {"category": "fruit", "name": "orange", "price": 4}
        ]
        expected1 = [
            {"category": "fruit", "name": "banana", "price": 2},
            {"category": "fruit", "name": "apple", "price": 3},
            {"category": "fruit", "name": "orange", "price": 4},
            {"category": "vegetable", "name": "carrot", "price": 1}
        ]
        result1 = hierarchical_sort.hierarchical_sort(
            data1,
            [('category', 'asc'), ('name', 'asc')]
        )
        assert result1 == expected1
        record_result("Normal multi-level sort on dicts", True)
    except AssertionError:
        record_result("Normal multi-level sort on dicts", False, "Result mismatch")
    except Exception as e:
        record_result("Normal multi-level sort on dicts", False, str(e))
    
    # 2. Edge case: empty dataset
    try:
        data2 = []
        result2 = hierarchical_sort.hierarchical_sort(data2, [('category', 'asc')])
        assert result2 == []
        record_result("Empty dataset", True)
    except AssertionError:
        record_result("Empty dataset", False, "Result not empty list")
    except Exception as e:
        record_result("Empty dataset", False, str(e))
    
    # 3. Edge case: dataset with one item
    try:
        data3 = [{"category": "fruit", "name": "apple", "price": 3}]
        result3 = hierarchical_sort.hierarchical_sort(data3, [('category', 'asc')])
        assert result3 == data3
        record_result("Single item dataset", True)
    except AssertionError:
        record_result("Single item dataset", False, "Result changed for single item")
    except Exception as e:
        record_result("Single item dataset", False, str(e))
    
    # 4. Error condition: invalid data type (not list)
    try:
        invalid_data = "not a list"
        hierarchical_sort.hierarchical_sort(invalid_data, [('category', 'asc')])
        record_result("Invalid data type (not list)", False, "No exception raised")
    except TypeError:
        record_result("Invalid data type (not list)", True)
    except