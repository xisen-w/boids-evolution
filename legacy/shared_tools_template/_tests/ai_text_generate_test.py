import sys
import os
import json
from datetime import datetime


def run_tests():
    """Run tests for ai_text_generate (simplified API)."""
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
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        tools_dir = os.path.dirname(tests_dir)
        project_root = os.path.dirname(tools_dir)
        for p in [tools_dir, project_root]:
            if p not in sys.path:
                sys.path.insert(0, p)
        import ai_text_generate
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record(name, passed, detail=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        entry = {"name": name, "passed": passed}
        if detail is not None:
            entry["detail"] = detail
        results["tests"].append(entry)

    has_azure = bool(os.getenv("AZURE_OPENAI_API_KEY")) and bool(os.getenv("AZURE_OPENAI_ENDPOINT"))

    if not has_azure:
        record("env_missing_skipped", True, "Azure credentials not set; skipping live calls")
    else:
        # Test 1: basic generation
        try:
            text = ai_text_generate.execute("Write a short story about a robot learning to paint.")
            passed = isinstance(text, str)
            record("basic_generation", passed)
        except Exception as e:
            record("basic_generation", False, str(e))

        # Test 2: style + temperature
        try:
            text = ai_text_generate.execute("Describe a magical forest.", temperature=0.8, max_tokens=120, style="creative")
            passed = isinstance(text, str)
            record("style_and_temperature", passed)
        except Exception as e:
            record("style_and_temperature", False, str(e))

    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2)) 