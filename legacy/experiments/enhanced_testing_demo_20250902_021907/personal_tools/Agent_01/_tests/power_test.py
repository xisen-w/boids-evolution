import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for power"""
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
        sys.path.append(os.path.dirname(__file__))
        import power
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
    
    # Test 1: Normal usage - positive integers
    try:
        output = power.execute(2, 3)
        if output == 8:
            record_result("Normal usage positive integers", True)
        else:
            record_result("Normal usage positive integers", False, f"Expected 8, got {output}")
    except Exception as e:
        record_result("Normal usage positive integers", False, str(e))
    
    # Test 2: Zero exponent
    try:
        output = power.execute(5, 0)
        if output == 1:
            record_result("Zero exponent", True)
        else:
            record_result("Zero exponent", False, f"Expected 1, got {output}")
    except Exception as e:
        record_result("Zero exponent", False, str(e))
    
    # Test 3: Negative base with positive exponent
    try:
        output = power.execute(-2, 3)
        if output == -8:
            record_result("Negative base positive exponent", True)
        else:
            record_result("Negative base positive exponent", False, f"Expected -8, got {output}")
    except Exception as e:
        record_result("Negative base positive exponent", False, str(e))
    
    # Test 4: Negative exponent (should raise error or handle)
    try:
        output = power.execute(2, -3)
        # Assuming the function should raise an error for negative exponents
        record_result("Negative exponent", False, "Expected exception for negative exponent, got output")
    except Exception:
        record_result("Negative exponent", True)
    
    # Test 5: Non-integer base
    try:
        output = power.execute(2.5, 3)
        # Assuming the function should handle float base
        if abs(output - 15.625) < 1e-9:
            record_result("Float base positive exponent", True)
        else:
            record_result("Float base positive exponent", False, f"Expected 15.625, got {output}")
    except Exception as e:
        record_result("Float base positive exponent", False, str(e))
    
    # Test 6: Non-integer exponent (should raise error or handle)
    try:
        output = power.execute(2, 2.5)
        # Assuming the function should raise an error for non-integer exponent
        record_result("Non-integer exponent", False, "Expected exception for non-integer exponent, got output")
    except Exception:
        record_result("Non-integer exponent", True)
    
    # Test 7: Large numbers
    try:
        output = power.execute(2, 30)
        if output == 1073741824:
            record_result("Large exponent", True)
        else:
            record_result("Large exponent", False, f