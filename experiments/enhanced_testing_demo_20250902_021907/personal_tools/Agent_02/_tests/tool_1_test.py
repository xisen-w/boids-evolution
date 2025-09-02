import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for tool_1"""
    results = {
        "tool_name": "tool_1",
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
        import tool_1
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record_result(test_name, passed, error_message=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({
            "test_name": test_name,
            "passed": passed,
            "error_message": error_message
        })

    # Test 1: Normal usage with positive numbers
    try:
        input_data = {"numbers": [10, 20, 30, 40]}
        output = tool_1.execute(input_data)
        expected_mean = sum(input_data["numbers"]) / len(input_data["numbers"])
        if isinstance(output, dict) and abs(output.get("mean", 0) - expected_mean) < 1e-6:
            record_result("Normal usage with positive numbers", True)
        else:
            record_result("Normal usage with positive numbers", False, f"Unexpected output: {output}")
    except Exception as e:
        record_result("Normal usage with positive numbers", False, str(e))
    
    # Test 2: Edge case with empty list
    try:
        input_data = {"numbers": []}
        output = tool_1.execute(input_data)
        record_result("Edge case with empty list", False, f"Expected exception, got output: {output}")
    except Exception as e:
        # Expecting an exception due to division by zero or invalid input
        record_result("Edge case with empty list", True)
    
    # Test 3: Negative and zero values
    try:
        input_data = {"numbers": [-5, 0, 5]}
        expected_mean = sum(input_data["numbers"]) / len(input_data["numbers"])
        output = tool_1.execute(input_data)
        if isinstance(output, dict) and abs(output.get("mean", 0) - expected_mean) < 1e-6:
            record_result("Negative and zero values", True)
        else:
            record_result("Negative and zero values", False, f"Unexpected output: {output}")
    except Exception as e:
        record_result("Negative and zero values", False, str(e))
    
    # Test 4: Invalid parameter type (non-list)
    try:
        input_data = {"numbers": "not a list"}
        output = tool_1.execute(input_data)
        record_result("Invalid parameter type (non-list)", False, f"Expected exception, got output: {output}")
    except Exception as e:
        record_result("Invalid parameter type (non-list)", True)
    
    # Test 5: List with non-numeric values
    try:
        input_data = {"numbers": [1, 2, "three"]}
        output = tool_1.execute(input_data)
        record_result("List with non-numeric values", False, f"Expected exception, got output: {output}")
    except Exception as e:
        record_result("List with non-numeric values", True)

    # Finalize results
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results =