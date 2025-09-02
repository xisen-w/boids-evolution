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
            record_result("Normal usage positive integers", True)
        else:
            record_result("Normal usage positive integers", False, f"Expected 12, got {output}")
    except Exception as e:
        record_result("Normal usage positive integers", False, str(e))
    
    # Test 2: Normal usage with negative numbers
    try:
        output = multiply.execute(-5, 6)
        if output == -30:
            record_result("Negative and positive", True)
        else:
            record_result("Negative and positive", False, f"Expected -30, got {output}")
    except Exception as e:
        record_result("Negative and positive", False, str(e))
    
    # Test 3: Zero as input
    try:
        output = multiply.execute(0, 100)
        if output == 0:
            record_result("Zero input", True)
        else:
            record_result("Zero input", False, f"Expected 0, got {output}")
    except Exception as e:
        record_result("Zero input", False, str(e))
    
    # Test 4: Floating point numbers
    try:
        output = multiply.execute(2.5, 4)
        if abs(output - 10.0) < 1e-9:
            record_result("Floating point numbers", True)
        else:
            record_result("Floating point numbers", False, f"Expected 10.0, got {output}")
    except Exception as e:
        record_result("Floating point numbers", False, str(e))
    
    # Test 5: Large numbers (edge case)
    try:
        large_num = 10**18
        output = multiply.execute(large_num, 2)
        if output == large_num * 2:
            record_result("Large numbers", True)
        else:
            record_result("Large numbers", False, f"Expected {large_num*2}, got {output}")
    except Exception as e:
        record_result("Large numbers", False, str(e))
    
    # Test 6: Invalid input types (string)
    try:
        multiply.execute("a", 5)
        record_result("Invalid input string", False, "Expected exception but none raised")
    except Exception:
        record_result("Invalid input string", True)
    
    # Test 7: Missing parameters (simulate by passing None)
    try:
        multiply.execute(None, 5)
        record_result("None as first parameter", False, "Expected exception but none raised")
    except Exception:
        record_result("None as first parameter", True)
    
    # Finalize results
    results["all_passed"] = results["failed_tests"] ==