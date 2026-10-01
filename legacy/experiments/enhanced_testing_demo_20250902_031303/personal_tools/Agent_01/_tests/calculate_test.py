import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for calculate"""
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
        sys.path.append(os.path.dirname(__file__))
        import calculate
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
    
    # 1. Normal usage: addition
    try:
        output = calculate.execute("add", 5, 3)
        if output == 8:
            record_result("Addition normal", True)
        else:
            record_result("Addition normal", False, f"Expected 8, got {output}")
    except Exception as e:
        record_result("Addition normal", False, str(e))
    
    # 2. Normal usage: subtraction
    try:
        output = calculate.execute("subtract", 10, 4)
        if output == 6:
            record_result("Subtraction normal", True)
        else:
            record_result("Subtraction normal", False, f"Expected 6, got {output}")
    except Exception as e:
        record_result("Subtraction normal", False, str(e))
    
    # 3. Edge case: division by zero
    try:
        output = calculate.execute("divide", 10, 0)
        record_result("Division by zero", False, f"Expected exception, got {output}")
    except ZeroDivisionError:
        record_result("Division by zero", True)
    except Exception as e:
        record_result("Division by zero", False, f"Unexpected exception: {str(e)}")
    
    # 4. Edge case: large numbers multiplication
    try:
        large_num1 = 10**12
        large_num2 = 10**12
        output = calculate.execute("multiply", large_num1, large_num2)
        expected = large_num1 * large_num2
        if output == expected:
            record_result("Large numbers multiplication", True)
        else:
            record_result("Large numbers multiplication", False, f"Expected {expected}, got {output}")
    except Exception as e:
        record_result("Large numbers multiplication", False, str(e))
    
    # 5. Error condition: invalid operation
    try:
        output = calculate.execute("modulo", 10, 3)
        record_result("Invalid operation", False, f"Expected exception, got {output}")
    except ValueError:
        record_result("Invalid operation", True)
    except Exception as e:
        record_result("Invalid operation", False, f"Unexpected exception: {str(e)}")
    
    # 6. Parameter validation: missing parameters
    try:
        output = calculate.execute("add", None, 5)
        record_result("Missing parameter", False, f"Expected exception, got {output}")
    except TypeError:
        record_result("Missing parameter", True)
    except Exception as e:
        record_result("Missing parameter", False, f"Unexpected exception: {str(e)}")
    
    # 7. Negative numbers
    try:
        output = calculate.execute("subtract", -10, -5)
        if output == -5: