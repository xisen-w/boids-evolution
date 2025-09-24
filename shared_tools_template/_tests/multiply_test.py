import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run comprehensive tests for multiply tool"""
    results = {
        "tool_name": "multiply",
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
        import multiply
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {"name": "test_positive_numbers", "params": {"a": 6, "b": 7}, "expected": 42.0},
        {"name": "test_negative_numbers", "params": {"a": -4, "b": 5}, "expected": -20.0},
        {"name": "test_zero_multiplication", "params": {"a": 0, "b": 100}, "expected": 0.0},
        {"name": "test_decimal_numbers", "params": {"a": 2.5, "b": 4}, "expected": 10.0},
        {"name": "test_string_numbers", "params": {"a": "3", "b": "4"}, "expected": 12.0},
        {"name": "test_large_numbers", "params": {"a": 1000, "b": 1000}, "expected": 1000000.0},
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            params = test_case["params"]
            result = multiply.execute(params["a"], params["b"])

            passed = abs(result - test_case["expected"]) < 1e-6
            
            results["tests"].append({
                "name": test_case["name"],
                "passed": passed,
                "expected": test_case["expected"],
                "actual": result
            })
            
            if passed:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                
        except Exception as e:
            results["tests"].append({
                "name": test_case["name"],
                "passed": False,
                "error": str(e)
            })
            results["failed_tests"] += 1
    
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))
