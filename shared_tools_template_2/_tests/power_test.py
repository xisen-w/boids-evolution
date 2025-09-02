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
        {"name": "test_basic_power", "params": {"base": 2, "exponent": 3}, "expected": 8},
        {"name": "test_power_of_one", "params": {"base": 5, "exponent": 1}, "expected": 5},
        {"name": "test_power_of_zero", "params": {"base": 10, "exponent": 0}, "expected": 1},
        {"name": "test_zero_base", "params": {"base": 0, "exponent": 5}, "expected": 0},
        {"name": "test_negative_base", "params": {"base": -2, "exponent": 2}, "expected": 4},
        {"name": "test_negative_base_odd", "params": {"base": -2, "exponent": 3}, "expected": -8},
        {"name": "test_decimal_base", "params": {"base": 2.5, "exponent": 2}, "expected": 6.25},
        {"name": "test_large_exponent", "params": {"base": 2, "exponent": 10}, "expected": 1024},
        {"name": "test_negative_exponent", "params": {"base": 2, "exponent": -1}, "expected": "error"},
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = power.execute(test_case["params"])
            
            if test_case["expected"] == "error":
                passed = not result.get("success", True)
            else:
                # Check numeric_result field
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
