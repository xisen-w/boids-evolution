import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for KeywordExtractor"""
    results = {
        "tool_name": "KeywordExtractor",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Attempt to import the KeywordExtractor module
    try:
        sys.path.append(os.path.dirname(__file__))
        import KeywordExtractor
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

    # Test 1: Normal usage with typical text
    try:
        text = "Natural language processing enables computers to understand human language."
        output = KeywordExtractor.KeywordExtractor(text=text, top_n=3)
        assert isinstance(output, list), "Output is not a list"
        assert len(output) == 3, "Output length mismatch"
        for item in output:
            assert "keyword" in item and "score" in item, "Missing keys in output item"
            assert isinstance(item["keyword"], str), "Keyword is not a string"
            assert isinstance(item["score"], float), "Score is not a float"
        record_result("Normal usage with typical text", True)
    except Exception as e:
        record_result("Normal usage with typical text", False, str(e))

    # Test 2: Edge case with empty string input
    try:
        output = KeywordExtractor.KeywordExtractor(text="", top_n=5)
        assert isinstance(output, list), "Output is not a list"
        assert len(output) == 0, "Expected empty list for empty input"
        record_result("Empty string input", True)
    except Exception as e:
        record_result("Empty string input", False, str(e))

    # Test 3: Edge case with very large input text
    try:
        large_text = "word " * 10000  # repeated word to simulate large input
        output = KeywordExtractor.KeywordExtractor(text=large_text, top_n=5)
        assert isinstance(output, list), "Output is not a list"
        assert len(output) <= 5, "Output exceeds top_n limit"
        for item in output:
            assert "keyword" in item and "score" in item, "Missing keys in output item"
        record_result("Large input text", True)
    except Exception as e:
        record_result("Large input text", False, str(e))

    # Test 4: Invalid parameter types
    try:
        # Passing non-string as text
        try:
            KeywordExtractor.KeywordExtractor(text=12345)
            record_result("Invalid text parameter type", False, "Did not raise error for non-string text")
        except:
            record_result("Invalid text parameter type", True)
        # Passing non-integer top_n
        try:
            KeywordExtractor.KeywordExtractor(text="test", top_n="five")
            record_result("Invalid top_n parameter type", False, "Did not raise error for non-integer top_n")
        except:
            record_result("Invalid top_n parameter type", True)
        # Passing invalid language code
        try:
            KeywordExtractor.KeywordExtractor(text="test", language=123)
            record_result("Invalid language parameter type", False, "Did not raise error for non-string language")
        except:
            record_result("Invalid language parameter