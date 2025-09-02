import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for Agent_02_tool_1"""
    results = {
        "tool_name": "Agent_02_tool_1",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Import the tool
    try:
        sys.path.append(os.path.dirname(__file__))
        import Agent_02_tool_1
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    def record_result(test_name, passed, error_msg=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error_msg
        })
    
    # Test 1: Normal usage with positive integers
    try:
        input_values = [1, 2, 3, 4, 5]
        expected_mean = sum(input_values) / len(input_values)
        output = Agent_02_tool_1.execute(input_values)
        if abs(output - expected_mean) < 1e-8:
            record_result("Normal usage with positive integers", True)
        else:
            record_result("Normal usage with positive integers", False, f"Expected {expected_mean}, got {output}")
    except Exception as e:
        record_result("Normal usage with positive integers", False, str(e))
    
    # Test 2: Edge case with empty list
    try:
        input_values = []
        output = Agent_02_tool_1.execute(input_values)
        # Expecting None or error; assuming tool returns None for empty list
        if output is None:
            record_result("Empty list input", True)
        else:
            record_result("Empty list input", False, f"Expected None, got {output}")
    except Exception as e:
        record_result("Empty list input", False, str(e))
    
    # Test 3: List with negative and float numbers
    try:
        input_values = [-2.5, 0, 4.5]
        expected_mean = sum(input_values) / len(input_values)
        output = Agent_02_tool_1.execute(input_values)
        if abs(output - expected_mean) < 1e-8:
            record_result("Mixed negative and float numbers", True)
        else:
            record_result("Mixed negative and float numbers", False, f"Expected {expected_mean}, got {output}")
    except Exception as e:
        record_result("Mixed negative and float numbers", False, str(e))
    
    # Test 4: Invalid input - list with non-numeric values
    try:
        input_values = [1, 'a', 3]
        output = Agent_02_tool_1.execute(input_values)
        record_result("Non-numeric values in list", False, "Expected exception but got output")
    except Exception:
        record_result("Non-numeric values in list", True)
    
    # Test 5: Parameter validation - passing None
    try:
        input_values = None
        output = Agent_02_tool_1.execute(input_values)
        record_result("Parameter validation with None", False, "Expected exception but got output")
    except Exception:
        record_result("Parameter validation with None", True)
    
    # Finalize results
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps