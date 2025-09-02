import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run comprehensive tests for calculate tool"""
    results = {
        "tool_name": "calculate",
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
        import calculate
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        # Test addition
        {"name": "test_addition", "params": {"operation": "add", "a": 5, "b": 3}, "expected": 8},
        {"name": "test_subtraction", "params": {"operation": "subtract", "a": 10, "b": 4}, "expected": 6},
        {"name": "test_multiplication", "params": {"operation": "multiply", "a": 7, "b": 6}, "expected": 42},
        {"name": "test_division", "params": {"operation": "divide", "a": 15, "b": 3}, "expected": 5},
        {"name": "test_division_by_zero", "params": {"operation": "divide", "a": 10, "b": 0}, "expected": "error"},
        {"name": "test_default_operation", "params": {"a": 2, "b": 3}, "expected": 5},  # defaults to add
        {"name": "test_invalid_operation", "params": {"operation": "power", "a": 2, "b": 3}, "expected": "error"},
        {"name": "test_string_numbers", "params": {"operation": "add", "a": "5.5", "b": "2.5"}, "expected": 8.0},
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = calculate.execute(test_case["params"])
            
            if test_case["expected"] == "error":
                # Expect an error result
                passed = not result.get("success", True)
            else:
                # Expect successful result
                passed = (result.get("success") and 
                         abs(float(result.get("result", "").split(" = ")[-1]) - test_case["expected"]) < 0.001)
            
            # Clean result by removing outdated energy_gain
            clean_result = {k: v for k, v in result.items() if k != "energy_gain"}
            
            results["tests"].append({
                "name": test_case["name"],
                "passed": passed,
                "expected": test_case["expected"],
                "actual": clean_result
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
