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

    # 1. Normal usage: generate a random number within a range
    try:
        output = random_gen.execute(action='generate_number', min_value=1, max_value=10)
        if isinstance(output, int) and 1 <= output <= 10:
            record_result("Normal generate_number within range", True)
        else:
            record_result("Normal generate_number within range", False, "Output not in expected range or type")
    except Exception as e:
        record_result("Normal generate_number within range", False, str(e))
    
    # 2. Normal usage: make a random choice from a list
    try:
        choices = ['apple', 'banana', 'cherry']
        output = random_gen.execute(action='choose', options=choices)
        if output in choices:
            record_result("Normal choose from list", True)
        else:
            record_result("Normal choose from list", False, "Output not in options list")
    except Exception as e:
        record_result("Normal choose from list", False, str(e))
    
    # 3. Edge case: generate number with min == max
    try:
        output = random_gen.execute(action='generate_number', min_value=5, max_value=5)
        if output == 5:
            record_result("Edge case generate_number with min==max", True)
        else:
            record_result("Edge case generate_number with min==max", False, "Output not equal to min/max")
    except Exception as e:
        record_result("Edge case generate_number with min==max", False, str(e))
    
    # 4. Error condition: missing required parameters
    try:
        output = random_gen.execute(action='generate_number', min_value=1)
        record_result("Missing max_value parameter", False, "Expected error but got output")
    except TypeError:
        record_result("Missing max_value parameter", True)
    except Exception as e:
        record_result("Missing max_value parameter", False, f"Unexpected error: {str(e)}")
    
    # 5. Error condition: invalid action
    try:
        output = random_gen.execute(action='invalid_action')
        record_result("Invalid action parameter", False, "Expected error but got output")
    except ValueError:
        record_result("Invalid action parameter", True)
    except Exception as e:
        record_result("Invalid action parameter", False, f"Unexpected error: {str(e)}")
    
    # 6. Parameter validation: options not a list
    try:
        output = random_gen.execute(action='choose', options='notalist')
        record_result("Options parameter not list", False, "Expected error but got output")
    except TypeError:
        record_result("Options parameter not list", True)
    except Exception as e:
        record_result("Options