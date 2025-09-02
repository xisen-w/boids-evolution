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
    
    def record_test(name, expected, actual):
        results["total_tests"] += 1
        if expected == actual:
            results["passed_tests"] += 1
            results["tests"].append({"name": name, "status": "passed", "expected": expected, "actual": actual})
        else:
            results["failed_tests"] += 1
            results["tests"].append({"name": name, "status": "failed", "expected": expected, "actual": actual})
    
    # Test 1: Normal usage - positive integers
    try:
        result = power.execute(2, 3)
        record_test("Normal usage positive integers", 8, result)
    except Exception as e:
        record_test("Normal usage positive integers", "Error: " + str(e), "Error: " + str(e))
    
    # Test 2: Zero exponent
    try:
        result = power.execute(5, 0)
        record_test("Zero exponent", 1, result)
    except Exception as e:
        record_test("Zero exponent", "Error: " + str(e), "Error: " + str(e))
    
    # Test 3: Zero base with positive exponent
    try:
        result = power.execute(0, 4)
        record_test("Zero base positive exponent", 0, result)
    except Exception as e:
        record_test("Zero base positive exponent", "Error: " + str(e), "Error: " + str(e))
    
    # Test 4: Negative base with integer exponent
    try:
        result = power.execute(-2, 3)
        record_test("Negative base odd exponent", -8, result)
    except Exception as e:
        record_test("Negative base odd exponent", "Error: " + str(e), "Error: " + str(e))
    
    # Test 5: Negative exponent (should raise error or handle accordingly)
    try:
        result = power.execute(2, -3)
        # Assuming the function should raise an error for negative exponents
        record_test("Negative exponent", "Error", result)
    except Exception as e:
        record_test("Negative exponent", "Error", "Error")
    
    # Test 6: Non-integer base (float)
    try:
        result = power.execute(2.5, 3)
        # Assuming the function supports float base
        expected = 2.5 ** 3
        record_test("Float base", expected, result)
    except Exception as e:
        record_test("Float base", "Error: " + str(e), "Error: " + str(e))
    
    # Test 7: Non-integer exponent (float)
    try:
        result = power.execute(2, 2.5)
        # Assuming the function supports float exponent
        expected = 2 ** 2.5
        record_test("Float exponent", expected, result)
    except Exception as e:
        record_test("Float exponent", "Error: " + str(e), "Error: " + str(e))
    
    # Test 8: Negative base with fractional exponent (complex result)
    try:
        result = power.execute(-4, 0