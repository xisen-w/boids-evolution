import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_tests():
    """Run comprehensive tests for ai_text_generate tool"""
    results = {
        "tool_name": "ai_text_generate",
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
        import ai_text_generate
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {
            "name": "test_basic_text_generation",
            "params": {"prompt": "Write a short story about a robot learning to paint."},
            "check_type": "success_and_content"
        },
        {
            "name": "test_creative_style",
            "params": {
                "prompt": "Describe a magical forest.",
                "style": "creative",
                "temperature": 0.8,
                "max_tokens": 150
            },
            "check_type": "success_and_content"
        },
        {
            "name": "test_professional_style",
            "params": {
                "prompt": "Write a business email about a project update.",
                "style": "professional",
                "temperature": 0.3,
                "max_tokens": 100
            },
            "check_type": "success_and_content"
        },
        {
            "name": "test_technical_style",
            "params": {
                "prompt": "Explain how machine learning works.",
                "style": "technical",
                "max_tokens": 200
            },
            "check_type": "success_and_content"
        },
        {
            "name": "test_humorous_style",
            "params": {
                "prompt": "Write a funny story about a programmer and a bug.",
                "style": "humorous",
                "temperature": 0.9
            },
            "check_type": "success_and_content"
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
        },
        {
            "name": "test_parameter_validation",
            "params": {
                "prompt": "Test prompt",
                "temperature": 2.0,  # Should be clamped to 1.0
                "max_tokens": 2000   # Should be clamped to 1000
            },
            "check_type": "parameter_validation"
        }
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = ai_text_generate.execute(test_case["params"])
            
            if test_case["check_type"] == "success_and_content":
                # Check for successful generation with content
                passed = (
                    result.get("success") == True and
                    "result" in result and
                    len(result["result"]) > 10 and  # Non-trivial content
                    "word_count" in result and
                    "char_count" in result and
                    "settings" in result
                )
                
                # Additional checks for style-specific tests
                if "style" in test_case["params"]:
                    passed = passed and result["settings"]["style"] == test_case["params"]["style"]
                
            elif test_case["check_type"] == "error_handling":
                # Should return error for missing/empty prompt
                passed = (
                    result.get("success") == False and
                    "error" in result
                )
                
            elif test_case["check_type"] == "parameter_validation":
                # Check that parameters were properly validated/clamped
                passed = (
                    result.get("success") == True and
                    result["settings"]["temperature"] <= 1.0 and
                    result["settings"]["max_tokens"] <= 1000
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