import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for square"""
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
        sys.path.append(os.path.dirname(__file__))
        import square
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

    # Test 1: Normal usage with positive integer
    try:
        output = square.execute(4)
        expected = 16
        if output == expected:
            record_result("Normal positive integer", True)
        else:
            record_result("Normal positive integer", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Normal positive integer", False, str(e))
    
    # Test 2: Normal usage with negative integer
    try:
        output = square.execute(-3)
        expected = 9
        if output == expected:
            record_result("Negative integer", True)
        else:
            record_result("Negative integer", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Negative integer", False, str(e))
    
    # Test 3: Edge case with zero
    try:
        output = square.execute(0)
        expected = 0
        if output == expected:
            record_result("Zero input", True)
        else:
            record_result("Zero input", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Zero input", False, str(e))
    
    # Test 4: Floating point input
    try:
        output = square.execute(2.5)
        expected = 6.25
        if abs(output - expected) < 1e-9:
            record_result("Floating point input", True)
        else:
            record_result("Floating point input", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Floating point input", False, str(e))
    
    # Test 5: Invalid input (string)
    try:
        output = square.execute("test")
        record_result("Invalid string input", False, f"Expected exception, got {output}")
    except Exception:
        record_result("Invalid string input", True)
    
    # Test 6: Invalid input (None)
    try:
        output = square.execute(None)
        record_result("None input", False, f"Expected exception, got {output}")
    except Exception:
        record_result("None input", True)
    
    # Test 7: Large number
    try:
        large_num = 10**10
        output = square.execute(large_num)
        expected = large_num ** 2
        if output == expected:
            record_result("Large number input", True)
        else:
            record_result("Large number input", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Large number input", False, str(e))
    
    # Final check
    results["all_passed"] = results["failed_tests"] == 0
    return results

if