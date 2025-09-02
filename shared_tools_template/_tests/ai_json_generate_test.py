import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run comprehensive tests for ai_json_generate tool"""
    results = {
        "tool_name": "ai_json_generate",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Import the tool
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import ai_json_generate
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {
            "name": "test_basic_json_object",
            "params": {
                "prompt": "Generate a user profile with name, age, email, and preferences",
                "format_type": "object"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_json_array",
            "params": {
                "prompt": "Generate an array of 3 product items with id, name, and price",
                "format_type": "array"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_config_json",
            "params": {
                "prompt": "Generate a configuration file for a web server with port, host, database settings",
                "format_type": "config"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_api_response",
            "params": {
                "prompt": "Generate an API response for a user authentication endpoint",
                "format_type": "api"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_with_schema",
            "params": {
                "prompt": "Generate user data following this structure",
                "schema": '{"user": {"id": "string", "profile": {"name": "string", "settings": {}}}}',
                "format_type": "data"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_json_schema_generation",
            "params": {
                "prompt": "Generate a JSON schema for a blog post with title, content, author, and tags",
                "format_type": "schema"
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_temperature_control",
            "params": {
                "prompt": "Generate a simple configuration object",
                "temperature": 0.0  # Very consistent output
            },
            "check_type": "success_and_structure"
        },
        {
            "name": "test_no_prompt_error",
            "params": {},
            "check_type": "error_handling"
        },
        {
            "name": "test_empty_prompt_error",
            "params": {"prompt": ""},
            "check_type": "error_handling"
        }
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = ai_json_generate.execute(test_case["params"])
            
            if test_case["check_type"] == "success_and_structure":
                # Check for successful JSON generation with proper structure
                passed = (
                    result.get("success") == True and
                    "result" in result and
                    "json_string" in result and
                    "structure_info" in result and
                    "settings" in result
                )
                
                # Verify the result is actually valid JSON
                if passed:
                    try:
                        # Try to parse the json_string to ensure it's valid
                        parsed = json.loads(result["json_string"])
                        passed = passed and (parsed == result["result"])
                    except (json.JSONDecodeError, TypeError):
                        passed = False
                
                # Check format type if specified
                if "format_type" in test_case["params"]:
                    passed = passed and result["settings"]["format_type"] == test_case["params"]["format_type"]
                
                # Check structure info
                if passed and "structure_info" in result:
                    structure_info = result["structure_info"]
                    if test_case["params"].get("format_type") == "array":
                        passed = passed and structure_info["type"] == "list"
                    elif test_case["params"].get("format_type") in ["object", "config", "api", "data"]:
                        passed = passed and structure_info["type"] == "dict"
                
            elif test_case["check_type"] == "error_handling":
                # Should return error for missing/empty prompt
                passed = (
                    result.get("success") == False and
                    "error" in result
                )
            
            else:
                passed = result.get("success") == True
            
            # Clean result by removing any potential sensitive data
            clean_result = {k: v for k, v in result.items() if k not in ["api_key", "endpoint"]}
            
            results["tests"].append({
                "name": test_case["name"],
                "passed": passed,
                "check_type": test_case["check_type"],
                "actual": clean_result
            })
            
            if passed:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                
        except Exception as e:
            results["tests"].append({
                "name": test_case["name"],
                "passed": False,
                "error": str(e)
            })
            results["failed_tests"] += 1
    
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2)) 