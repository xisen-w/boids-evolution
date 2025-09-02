import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for statistical_summary"""
    results = {
        "tool_name": "statistical_summary",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the statistical_summary module
    try:
        sys.path.append(os.path.dirname(__file__))
        import statistical_summary
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

    # 1. Normal usage with a small dataset
    try:
        data = [1, 2, 3, 4, 5]
        output = statistical_summary.execute(data)
        expected = {
            "mean": 3.0,
            "median": 3.0,
            "variance": 2.5,
            "standard_deviation": 1.58
        }
        # Allow small floating point differences
        passed = all(
            abs(output[key] - expected[key]) < 0.01 for key in expected
        )
        record_result("Normal usage with small dataset", passed,
                      f"Output: {output}")
    except Exception as e:
        record_result("Normal usage with small dataset", False, str(e))
    
    # 2. Edge case: empty list should raise an error
    try:
        data = []
        output = statistical_summary.execute(data)
        record_result("Empty list input", False, "Expected exception, got output")
    except Exception:
        record_result("Empty list input", True)
    
    # 3. Edge case: single element list
    try:
        data = [42]
        output = statistical_summary.execute(data)
        expected = {
            "mean": 42.0,
            "median": 42.0,
            "variance": 0.0,
            "standard_deviation": 0.0
        }
        passed = all(
            abs(output[key] - expected[key]) < 0.0001 for key in expected
        )
        record_result("Single element list", passed, f"Output: {output}")
    except Exception as e:
        record_result("Single element list", False, str(e))
    
    # 4. Error condition: non-numeric data
    try:
        data = [1, 2, 'a', 4]
        output = statistical_summary.execute(data)
        record_result("Non-numeric data", False, "Expected exception, got output")
    except Exception:
        record_result("Non-numeric data", True)
    
    # 5. Parameter validation: passing None
    try:
        data = None
        output = statistical_summary.execute(data)
        record_result("None as input", False, "Expected exception, got output")
    except Exception:
        record_result("None as input", True)
    
    # 6. Large dataset
    try:
        data = list(range(1, 10001))
        output = statistical_summary.execute(data)
        # Known values for large range
        expected_mean = (1 + 10000) / 2
        expected_median = (5000 + 5001) / 2
        # Variance for uniform distribution
        n = len(data)
        mean = expected_mean