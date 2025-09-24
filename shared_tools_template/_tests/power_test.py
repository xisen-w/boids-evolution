import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run comprehensive tests for power tool"""
    results = {
        "tool_name": "power",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Import the tool
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import power
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {"name": "test_basic_power", "params": {"base": 2, "exponent": 3}, "expected": 8.0},
        {"name": "test_power_of_one", "params": {"base": 5, "exponent": 1}, "expected": 5.0},
        {"name": "test_power_of_zero", "params": {"base": 10, "exponent": 0}, "expected": 1.0},
        {"name": "test_zero_base", "params": {"base": 0, "exponent": 5}, "expected": 0.0},
        {"name": "test_negative_base", "params": {"base": -2, "exponent": 2}, "expected": 4.0},
        {"name": "test_negative_base_odd", "params": {"base": -2, "exponent": 3}, "expected": -8.0},
        {"name": "test_decimal_base", "params": {"base": 2.5, "exponent": 2}, "expected": 6.25},
        {"name": "test_large_exponent", "params": {"base": 2, "exponent": 10}, "expected": 1024.0},
        {"name": "test_negative_exponent", "params": {"base": 2, "exponent": -1}, "expect_error": ValueError},
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        params = test_case["params"]
        expected_error = test_case.get("expect_error")

        try:
            result = power.execute(params["base"], params["exponent"])
            if expected_error:
                passed = False
                actual = result
            else:
                passed = abs(result - test_case["expected"]) < 1e-6
                actual = result
        except Exception as exc:
            if expected_error and isinstance(exc, expected_error):
                passed = True
                actual = str(exc)
            else:
                passed = False
                actual = str(exc)

        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1

        results["tests"].append({
            "name": test_case["name"],
            "passed": passed,
            "expected": test_case.get("expected", str(expected_error)),
            "actual": actual
        })
    
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))
