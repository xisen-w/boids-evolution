import sys
import os
import json
import re
from datetime import datetime

def run_tests():
    """Run comprehensive tests for random_gen tool"""
    results = {
        "tool_name": "random_gen",
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
        import random_gen
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        # Test number generation
        {"name": "test_random_number", "params": {"type": "number", "min": 1, "max": 10}, "test_type": "range"},
        {"name": "test_random_number_negative", "params": {"type": "number", "min": -5, "max": 5}, "test_type": "range"},
        {"name": "test_random_number_float", "params": {"type": "number", "min": 1, "max": 2}, "test_type": "range"},
        
        # Test choice generation
        {"name": "test_random_choice", "params": {"type": "choice", "choices": ["apple", "banana", "cherry"]}, "test_type": "choice"},
        {"name": "test_random_choice_single", "params": {"type": "choice", "choices": ["only_option"]}, "test_type": "choice"},
        {"name": "test_random_choice_numbers", "params": {"type": "choice", "choices": [1, 2, 3, 4, 5]}, "test_type": "choice"},
        
        # Test edge cases
        {"name": "test_invalid_type", "params": {"type": "invalid"}, "test_type": "error"},
        {"name": "test_empty_choices", "params": {"type": "choice", "choices": []}, "test_type": "error"},
        {"name": "test_missing_min_max", "params": {"type": "number"}, "test_type": "range"},  # Should use defaults
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = random_gen.execute(test_case["params"])
            
            if test_case["test_type"] == "range":
                # Extract number from result string like "Random number between 1 and 10: 7"
                if result.get("success"):
                    match = re.search(r': (\d+)$', result.get("result", ""))
                    if match:
                        actual_number = int(match.group(1))
                        min_val = test_case["params"].get("min", 1)
                        max_val = test_case["params"].get("max", 100)
                        passed = min_val <= actual_number <= max_val
                    else:
                        passed = False
                else:
                    passed = False
                         
            elif test_case["test_type"] == "choice":
                # Extract choice from result string like "Random choice from ['apple', 'banana']: apple"
                if result.get("success"):
                    match = re.search(r': (.+)$', result.get("result", ""))
                    if match:
                        actual_choice = match.group(1)
                        choices = test_case["params"]["choices"]
                        # Convert to string for comparison since result is always string
                        str_choices = [str(c) for c in choices]
                        passed = actual_choice in str_choices
                    else:
                        passed = False
                else:
                    passed = False
                         
            elif test_case["test_type"] == "error":
                # Test if it properly handles errors
                passed = not result.get("success", True)
            else:
                passed = result.get("success", False)
            
            # Clean result by removing outdated energy_gain
            clean_result = {k: v for k, v in result.items() if k != "energy_gain"}
            
            results["tests"].append({
                "name": test_case["name"],
                "passed": passed,
                "test_type": test_case["test_type"],
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
