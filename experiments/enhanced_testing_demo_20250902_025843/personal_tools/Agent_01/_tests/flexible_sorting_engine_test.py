import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for flexible_sorting_engine"""
    results = {
        "tool_name": "flexible_sorting_engine",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": True
    }
    
    # Import the tool
    try:
        sys.path.append(os.path.dirname(__file__))
        import flexible_sorting_engine
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

    # Test 1: Normal multi-criteria sorting with grouping
    try:
        data = [
            {"name": "Alice", "score": 85, "category": "A"},
            {"name": "Bob", "score": 92, "category": "B"},
            {"name": "Charlie", "score": 85, "category": "A"},
            {"name": "David", "score": 92, "category": "A"}
        ]
        sort_keys = [("score", "desc"), ("name", "asc")]
        group_by = ["category"]
        sorted_result = flexible_sorting_engine.execute(
            data=data,
            sort_keys=sort_keys,
            group_by=group_by
        )
        # Expect grouping with sorted sublists
        expected_grouped = {
            "A": [
                {"name": "David", "score": 92, "category": "A"},
                {"name": "Charlie", "score": 85, "category": "A"},
                {"name": "Alice", "score": 85, "category": "A"}
            ],
            "B": [
                {"name": "Bob", "score": 92, "category": "B"}
            ]
        }
        assert isinstance(sorted_result, dict), "Result should be a dict when grouped"
        assert sorted_result.keys() == expected_grouped.keys(), "Group keys mismatch"
        for key in expected_grouped:
            assert sorted_result[key] == expected_grouped[key], f"Mismatch in group {key}"
        record_result("Normal multi-criteria sorting with grouping", True)
    except Exception as e:
        record_result("Normal multi-criteria sorting with grouping", False, str(e))
    
    # Test 2: Edge case - empty data list
    try:
        empty_data = []
        result = flexible_sorting_engine.execute(
            data=empty_data,
            sort_keys=[("score", "asc")]
        )
        assert result == [], "Empty data should return empty list"
        record_result("Empty data list", True)
    except Exception as e:
        record_result("Empty data list", False, str(e))
    
    # Test 3: Error - invalid sort order
    try:
        data = [{"name": "Eve", "score": 70}]
        flexible_sorting_engine.execute(
            data=data,
            sort_keys=[("score", "ascending")]
        )
        record_result("Invalid sort order", False, "Did not raise error for invalid order")
    except ValueError:
        record_result("Invalid sort order", True)
    except Exception as e:
        record_result("Invalid sort order", False, f"Unexpected error: {str(e)}")
    
    # Test