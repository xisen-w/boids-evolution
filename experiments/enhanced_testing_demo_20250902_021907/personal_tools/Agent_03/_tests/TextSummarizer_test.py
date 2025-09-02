import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for TextSummarizer"""
    results = {
        "tool_name": "TextSummarizer",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }

    # Attempt to import the TextSummarizer module
    try:
        sys.path.append(os.path.dirname(__file__))
        import TextSummarizer
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

    # Test 1: Normal usage with a typical paragraph
    try:
        input_text = ("Artificial intelligence (AI) is intelligence demonstrated by machines, "
                      "unlike the natural intelligence displayed by humans and animals. "
                      "Leading AI textbooks define the field as the study of 'intelligent agents': "
                      "any device that perceives its environment and takes actions that maximize "
                      "its chance of successfully achieving its goals.")
        result = TextSummarizer.execute(text=input_text, max_length=50)
        summary = result.get("summary", "")
        original_length = result.get("original_length")
        summary_length = result.get("summary_length")
        if ("AI" in summary or "intelligence" in summary) and isinstance(summary, str):
            record_result("Normal usage with typical paragraph", True)
        else:
            record_result("Normal usage with typical paragraph", False, "Unexpected summary content or type")
    except Exception as e:
        record_result("Normal usage with typical paragraph", False, str(e))

    # Test 2: Edge case with very short input text
    try:
        short_text = "Hello world!"
        result = TextSummarizer.execute(text=short_text)
        summary = result.get("summary", "")
        if isinstance(summary, str) and len(summary) > 0:
            record_result("Edge case with very short input", True)
        else:
            record_result("Edge case with very short input", False, "Empty or invalid summary")
    except Exception as e:
        record_result("Edge case with very short input", False, str(e))

    # Test 3: Error condition with empty string input
    try:
        empty_text = ""
        result = TextSummarizer.execute(text=empty_text)
        # Expecting an error or specific handling
        record_result("Error with empty input", False, "Expected exception or error handling for empty input")
    except Exception:
        # If exception is raised, test passes
        record_result("Error with empty input", True)
    except:
        record_result("Error with empty input", False, "Unexpected error type")

    # Test 4: Invalid parameter types (non-string text)
    try:
        invalid_input = 12345
        result = TextSummarizer.execute(text=invalid_input)
        record_result("Invalid parameter type (non-string)", False, "Expected exception for non-string input")
    except Exception:
        record_result("Invalid parameter type (non-string)", True)

    # Test 5: Custom max_length and min_length parameters
    try:
        long_text = ("Natural language processing (NLP) is a subfield of linguistics, computer science, "
                     "and artificial intelligence concerned with the interactions between computers and "
                     "human language,