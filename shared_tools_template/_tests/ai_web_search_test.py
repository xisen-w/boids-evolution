import sys
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# This is the standard test template, adapted for mocking.

def run_tests():
    """Run all tests for ai_web_search"""
    results = {
        "tool_name": "ai_web_search",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # CRITICAL: Use this EXACT import code
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        import ai_web_search
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
            "name": test_name,
            "passed": passed,
            "error": error_msg
        })

    # Mock TavilyClient for all tests in this function
    with patch('ai_web_search.TavilyClient') as MockTavilyClient:
        # Test Case 1: Successful search
        try:
            mock_instance = MockTavilyClient.return_value
            mock_instance.search.return_value = {"results": [{"title": "Mock Result", "content": "This is a test."}]}
            
            # Set a dummy API key for the test
            os.environ["TAVILY_API_KEY"] = "test_key"
            
            result = ai_web_search.execute({'query': 'what is emergent intelligence?'})
            if result and "results" in result and result["results"][0]["title"] == "Mock Result":
                record_result("Successful Search", True)
            else:
                record_result("Successful Search", False, f"Unexpected result: {result}")
        except Exception as e:
            record_result("Successful Search", False, str(e))

        # Test Case 2: API call fails
        try:
            mock_instance = MockTavilyClient.return_value
            mock_instance.search.side_effect = Exception("API Error")
            
            result = ai_web_search.execute({'query': 'a query that fails'})
            # This test passes if the tool handles the exception gracefully
            if "error" in result or not result.get("success", True):
                 record_result("API Failure Handling", True)
            else:
                 record_result("API Failure Handling", False, "Tool did not report an error on API failure.")

        except Exception as e:
            # The tool's internal try/except should prevent this, but we record it if it fails
            record_result("API Failure Handling", False, f"Tool crashed on API failure: {str(e)}")

        # Test Case 3: Missing API Key
        try:
            # Temporarily remove the key
            original_key = os.environ.pop("TAVILY_API_KEY", None)
            
            # Re-initialize the client inside the tool by re-importing or direct call if possible
            # For this tool, the client is initialized inside execute, so we just call it
            result = ai_web_search.execute({'query': 'test'})

            # The tool should ideally fail gracefully if the key is missing.
            # TavilyClient constructor might raise an error.
            record_result("Missing API Key", False, "Tool did not fail as expected with a missing API key.")

        except Exception as e:
            # This is the expected outcome - the tool fails because the key is missing.
            record_result("Missing API Key", True, f"Tool correctly failed with: {str(e)}")
        finally:
            # Restore the key
            if original_key:
                os.environ["TAVILY_API_KEY"] = original_key

    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2)) 