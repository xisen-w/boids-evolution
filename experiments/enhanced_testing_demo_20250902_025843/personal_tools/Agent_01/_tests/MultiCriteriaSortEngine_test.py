import sys
import os
import json
from datetime import datetime

def run_tests():
    results = {
        "tool_name": "MultiCriteriaSortEngine",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    # Attempt to import the tool module
    try:
        sys.path.append(os.path.dirname(__file__))
        import MultiCriteriaSortEngine
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

    # 1. Normal usage: sort list of dicts by age ascending, then name descending
    try:
        data1 = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 30},
            {'name': 'David', 'age': 25}
        ]
        sorted1 = MultiCriteriaSortEngine(
            data=data1,
            criteria=[
                (lambda x: x['age'], 'asc'),
                (lambda x: x['name'], 'desc')
            ],
            large_scale_support=False
        )
        expected1 = [
            {'name': 'David', 'age': 25},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 30},
            {'name': 'Alice', 'age': 30}
        ]
        if sorted1 == expected1:
            record_result("Normal usage - dicts by age asc, name desc", True)
        else:
            record_result("Normal usage - dicts by age asc, name desc", False, "Incorrect sorting result")
    except Exception as e:
        record_result("Normal usage - dicts by age asc, name desc", False, str(e))

    # 2. Edge case: empty dataset
    try:
        data2 = []
        sorted2 = MultiCriteriaSortEngine(
            data=data2,
            criteria=[
                (lambda x: x['value'], 'asc')
            ]
        )
        if sorted2 == []:
            record_result("Edge case - empty dataset", True)
        else:
            record_result("Edge case - empty dataset", False, "Expected empty list")
    except Exception as e:
        record_result("Edge case - empty dataset", False, str(e))

    # 3. Error condition: invalid data type (non-list)
    try:
        data3 = "not a list"
        MultiCriteriaSortEngine(
            data=data3,
            criteria=[
                (lambda x: x, 'asc')
            ]
        )
        record_result("Error - invalid data type (non-list)", False, "Did not raise error for invalid data type")
    except TypeError:
        record_result("Error - invalid data type (non-list)", True)
    except Exception as e:
        record_result("Error - invalid data type (non-list)", False, str(e))

    # 4. Error condition: invalid criteria format
    try:
        data4 = [{'val': 1}]
        MultiCriteriaSortEngine(
            data=data4,
            criteria=[
                "not a tuple"
            ]
        )
        record_result("Error - invalid criteria format", False, "Did not raise error for invalid criteria format")