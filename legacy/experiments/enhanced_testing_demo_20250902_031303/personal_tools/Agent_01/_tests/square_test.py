import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for square tool"""
    results = {
        "tool_name": "square",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }

    # Attempt to import the square module
    try:
        sys.path.append(os.path.dirname(__file__))
        import square
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

    # Test 1: Normal usage with positive integer
    try:
        input_value = 4
        expected_output = 16
        output = square.execute(input_value)
        if output == expected_output:
            record_result("Normal positive integer", True)
        else:
            record_result("Normal positive integer", False, f"Expected {expected_output}, got {output}")
    except Exception as e:
        record_result("Normal positive integer", False, str(e))

    # Test 2: Normal usage with zero
    try:
        input_value = 0
        expected_output = 0
        output = square.execute(input_value)
        if output == expected_output:
            record_result("Zero input", True)
        else:
            record_result("Zero input", False, f"Expected {expected_output}, got {output}")
    except Exception as e:
        record_result("Zero input", False, str(e))

    # Test 3: Negative number
    try:
        input_value = -3
        expected_output = 9
        output = square.execute(input_value)
        if output == expected_output:
            record_result("Negative number", True)
        else:
            record_result("Negative number", False, f"Expected {expected_output}, got {output}")
    except Exception as e:
        record_result("Negative number", False, str(e))

    # Test 4: Floating point number
    try:
        input_value = 2.5
        expected_output = 6.25
        output = square.execute(input_value)
        if abs(output - expected_output) < 1e-9:
            record_result("Floating point number", True)
        else:
            record_result("Floating point number", False, f"Expected {expected_output}, got {output}")
    except Exception as e:
        record_result("Floating point number", False, str(e))

    # Test 5: Invalid input (string)
    try:
        input_value = "test"
        output = square.execute(input_value)
        record_result("Invalid string input", False, "Expected exception but got output")
    except Exception:
        record_result("Invalid string input", True)

    # Test 6: Invalid input (None)
    try:
        input_value = None
        output = square.execute(input_value)
        record_result("None input", False, "Expected exception but got output")
    except Exception:
        record_result("None input", True)

    # Test 7: Large number
    try:
        input_value = 1e6
        expected_output = 1e12
        output = square.execute(input_value)
        if abs(output - expected_output) < 1e-3:
            record_result("Large number", True)
        else:
            record_result("Large number", False, f"Expected {expected_output