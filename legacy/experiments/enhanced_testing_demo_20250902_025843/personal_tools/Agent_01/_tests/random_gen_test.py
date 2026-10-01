import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for random_gen"""
    results = {
        "tool_name": "random_gen",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the tool
    try:
        sys.path.append(os.path.dirname(__file__))
        import random_gen
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

    # Test 1: Normal usage - generate a random number within a range
    try:
        output = random_gen.execute({"type": "number", "min": 1, "max": 10})
        if isinstance(output, (int, float)) and 1 <= output <= 10:
            record_result("Normal number generation within range", True)
        else:
            record_result("Normal number generation within range", False, "Output not within specified range")
    except Exception as e:
        record_result("Normal number generation within range", False, str(e))
    
    # Test 2: Normal usage - make a random choice from a list
    try:
        choices = ["apple", "banana", "cherry"]
        output = random_gen.execute({"type": "choice", "choices": choices})
        if output in choices:
            record_result("Normal choice selection", True)
        else:
            record_result("Normal choice selection", False, "Output not in choices list")
    except Exception as e:
        record_result("Normal choice selection", False, str(e))
    
    # Test 3: Edge case - generate number with min == max
    try:
        output = random_gen.execute({"type": "number", "min": 5, "max": 5})
        if output == 5:
            record_result("Edge case number min==max", True)
        else:
            record_result("Edge case number min==max", False, "Output not equal to min/max")
    except Exception as e:
        record_result("Edge case number min==max", False, str(e))
    
    # Test 4: Error condition - missing required parameters
    try:
        output = random_gen.execute({"type": "number"})
        record_result("Missing parameters for number", False, "Expected error but got output")
    except Exception:
        record_result("Missing parameters for number", True)
    
    # Test 5: Error condition - invalid type
    try:
        output = random_gen.execute({"type": "unknown"})
        record_result("Invalid type parameter", False, "Expected error but got output")
    except Exception:
        record_result("Invalid type parameter", True)
    
    # Test 6: Parameter validation - non-list choices
    try:
        output = random_gen.execute({"type": "choice", "choices": "notalist"})
        record_result("Choices parameter not list", False, "Expected error but got output")
    except Exception:
        record_result("Choices parameter not list", True)
    
    # Test 7: Edge case - generate number with min > max
    try:
        output = random_gen.execute({"type": "number", "min": 10, "max": 5})
        record_result("Number min > max", False, "Expected error but got