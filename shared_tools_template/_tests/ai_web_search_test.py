import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_tests():
    """Run comprehensive tests for ai_web_search tool"""
    results = {
        "tool_name": "ai_web_search",
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
        import ai_web_search
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    test_cases = [
        {
            "name": "test_basic_web_search",
            "params": {"query": "what is emergent intelligence?"},
            "check_type": "success_and_content"
        },
        {
            "name": "test_technical_search",
            "params": {"query": "machine learning algorithms for natural language processing"},
            "check_type": "success_and_content"
        },
        {
            "name": "test_current_events_search",
            "params": {"query": "latest developments in artificial intelligence 2024"},
            "check_type": "success_and_content"
        },
        {
            "name": "test_no_query_error",
            "params": {},
            "check_type": "error_handling"
        },
        {
            "name": "test_empty_query_error",
            "params": {"query": ""},
            "check_type": "error_handling"
        }
    ]
    
    for test_case in test_cases:
        results["total_tests"] += 1
        try:
            result = ai_web_search.execute(test_case["params"])
            
            if test_case["check_type"] == "success_and_content":
                # Check for successful search with content
                passed = (
                    result.get("success") == True and
                    "results" in result and
                    len(result["results"]) > 0 and
                    "query" in result and
                    "timestamp" in result
                )
                
                # Verify results have expected structure
                if passed and result["results"]:
                    first_result = result["results"][0]
                    passed = passed and "title" in first_result and "content" in first_result
                
            elif test_case["check_type"] == "error_handling":
                # Should return error for missing/empty query
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