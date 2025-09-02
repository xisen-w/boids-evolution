import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run comprehensive tests for square tool"""
    results = {
        "tool_name": "square",
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
        import square
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {"name": "test_positive_integer", "params": {"number": 5}, "expected": 25},
        {"name": "test_negative_integer", "params": {"number": -3}, "expected": 9},
        {"name": "test_zero", "params": {"number": 0}, "expected": 0},
        {"name": "test_decimal", "params": {"number": 2.5}, "expected": 6.25},
        {"name": "test_string_number", "params": {"number": "4"}, "expected": 16},
        {"name": "test_large_number", "params": {"number": 100}, "expected": 10000},
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = square.execute(test_case["params"])
            
            # Check numeric_result field instead of parsing result string
            passed = (result.get("success") and 
                     abs(result.get("numeric_result", 0) - test_case["expected"]) < 0.001)
            
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
