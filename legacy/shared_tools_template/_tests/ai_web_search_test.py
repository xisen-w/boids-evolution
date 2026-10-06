import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv


def run_tests():
    """Run tests for ai_web_search (typed API)."""
    results = {
        "tool_name": "ai_web_search",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }

    # Ensure project root on path and load .env
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(tests_dir)
    project_root = os.path.dirname(tools_dir)
    for p in [tools_dir, project_root]:
        if p not in sys.path:
            sys.path.insert(0, p)
    load_dotenv(os.path.join(project_root, ".env"))

    # Import the tool
    try:
        import ai_web_search
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

    # Test 1: concrete query - emergent intelligence
    try:
        resp = ai_web_search.execute("emergent intelligence")
        passed = isinstance(resp, dict) and isinstance(resp.get("results", []), list)
        if passed and resp.get("results"):
            first = resp["results"][0]
            # check typical fields if present
            passed = passed and isinstance(first, dict)
        record("emergent_intelligence_query", passed)
    except Exception as e:
        record("emergent_intelligence_query", False, str(e))

    # Test 2: technical query
    try:
        resp = ai_web_search.execute("machine learning algorithms for NLP")
        passed = isinstance(resp, dict) and isinstance(resp.get("results", []), list)
        record("technical_query", passed)
    except Exception as e:
        record("technical_query", False, str(e))

    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2)) 