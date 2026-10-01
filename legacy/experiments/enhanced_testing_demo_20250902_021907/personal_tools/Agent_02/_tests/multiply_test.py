import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for multiply"""
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
        sys.path.append(os.path.dirname(__file__))
        import multiply
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
        output = multiply.execute(3, 4)
        if output == 12:
            record_result("Normal positive integers", True)
        else:
            record_result("Normal positive integers", False, f"Expected 12, got {output}")
    except Exception as e:
        record_result("Normal positive integers", False, str(e))
    
    # Test 2: Normal usage with negative integers
    try:
        output = multiply.execute(-5, 6)
        if output == -30:
            record_result("Negative and positive integers", True)
        else:
            record_result("Negative and positive integers", False, f"Expected -30, got {output}")
    except Exception as e:
        record_result("Negative and positive integers", False, str(e))
    
    # Test 3: Zero as an operand
    try:
        output = multiply.execute(0, 123)
        if output == 0:
            record_result("Zero operand", True)
        else:
            record_result("Zero operand", False, f"Expected 0, got {output}")
    except Exception as e:
        record_result("Zero operand", False, str(e))
    
    # Test 4: Floating point numbers
    try:
        output = multiply.execute(2.5, 4)
        if abs(output - 10.0) < 1e-9:
            record_result("Floating point numbers", True)
        else:
            record_result("Floating point numbers", False, f"Expected 10.0, got {output}")
    except Exception as e:
        record_result("Floating point numbers", False, str(e))
    
    # Test 5: Invalid input types (string)
    try:
        multiply.execute("a", 5)
        record_result("Invalid input string", False, "Expected exception but none raised")
    except Exception:
        record_result("Invalid input string", True)
    
    # Test 6: Missing parameters
    try:
        multiply.execute(5)
        record_result("Missing second parameter", False, "Expected exception but none raised")
    except Exception:
        record_result("Missing second parameter", True)
    
    # Test 7: Both parameters invalid types
    try:
        multiply.execute(None, [])
        record_result("Both parameters invalid types", False, "Expected exception but none raised")
    except Exception:
        record_result("Both parameters invalid types", True)
    
    # Finalize results
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))