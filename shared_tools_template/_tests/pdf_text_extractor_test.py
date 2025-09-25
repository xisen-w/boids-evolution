import sys
import os
import json
from datetime import datetime

def run_tests():
    results = {
        "tool_name": "pdf_text_extractor",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }

    # Add project root to path for imports
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Import tool
    try:
        import pdf_text_extractor
    except Exception as e:
        results["import_error"] = str(e)
        return results

    def record(test_name, passed, detail=""):
        results["tests"].append({
            "name": test_name,
            "passed": passed,
            "detail": detail
        })
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1

    # Test 1: Shakespeare Sonnet PDF (small, text-based)
    try:
        resource_path = os.path.join(project_root, 'resources/task_8_sonnets_18.pdf')
        result = pdf_text_extractor.execute(resource_path, method="pdfplumber")
        
        passed = (
            isinstance(result, dict) and
            "text" in result and
            len(result["text"]) > 100 and  # Should have substantial text
            "Shakespeare" in result["text"] or "sonnet" in result["text"].lower() and
            result["metadata"]["total_pages"] > 0
        )
        record("shakespeare_sonnet_extraction", passed, f"Extracted {len(result.get('text', ''))} characters")
    except Exception as e:
        record("shakespeare_sonnet_extraction", False, str(e))

    # Test 2: Math Notes PDF (larger, academic content)
    try:
        resource_path = os.path.join(project_root, 'resources/task_6_maths_notes.pdf')
        result = pdf_text_extractor.execute(resource_path, method="pypdf2")
        
        passed = (
            isinstance(result, dict) and
            "text" in result and
            len(result["text"]) > 1000 and  # Should have substantial content
            result["metadata"]["total_pages"] > 5 and  # Academic paper should be multi-page
            any(keyword in result["text"].lower() for keyword in ["statistical", "inference", "probability", "theorem"])
        )
        record("math_notes_extraction", passed, f"Extracted {len(result.get('text', ''))} characters from {result.get('metadata', {}).get('total_pages', 0)} pages")
    except Exception as e:
        record("math_notes_extraction", False, str(e))

    # Test 3: Page Range Extraction
    try:
        resource_path = os.path.join(project_root, 'resources/task_7_journey_to_the_west.pdf')
        result = pdf_text_extractor.execute(resource_path, method="pdfplumber", page_range=(0, 2))
        
        passed = (
            isinstance(result, dict) and
            "text" in result and
            len(result["pages"]) <= 3 and  # Should only have 3 pages max (0, 1, 2)
            result["metadata"]["total_pages"] > 3  # But total should be much larger
        )
        record("page_range_extraction", passed, f"Extracted {len(result.get('pages', []))} pages from range (0,2)")
    except Exception as e:
        record("page_range_extraction", False, str(e))

    # Test 4: Both Methods Comparison
    try:
        resource_path = os.path.join(project_root, 'resources/task_8_sonnets_18.pdf')
        result = pdf_text_extractor.execute(resource_path, method="both")
        
        passed = (
            isinstance(result, dict) and
            "text" in result and  # pdfplumber text
            "pypdf2_text" in result and  # pypdf2 text
            len(result["text"]) > 50 and
            len(result["pypdf2_text"]) > 50
        )
        record("both_methods_comparison", passed, f"pdfplumber: {len(result.get('text', ''))} chars, pypdf2: {len(result.get('pypdf2_text', ''))} chars")
    except Exception as e:
        record("both_methods_comparison", False, str(e))

    # Test 5: File Not Found Error Handling
    try:
        result = pdf_text_extractor.execute("nonexistent_file.pdf")
        passed = False  # Should raise an exception
        record("file_not_found_handling", passed, "Should have raised FileNotFoundError")
    except FileNotFoundError:
        record("file_not_found_handling", True, "Correctly raised FileNotFoundError")
    except Exception as e:
        record("file_not_found_handling", False, f"Wrong exception type: {str(e)}")

    # Test 6: Clean Text Option
    try:
        resource_path = os.path.join(project_root, 'resources/task_8_sonnets_18.pdf')
        result_clean = pdf_text_extractor.execute(resource_path, clean_text=True)
        result_raw = pdf_text_extractor.execute(resource_path, clean_text=False)
        
        passed = (
            isinstance(result_clean, dict) and
            isinstance(result_raw, dict) and
            "text" in result_clean and
            "text" in result_raw and
            len(result_clean["text"]) > 0 and
            len(result_raw["text"]) > 0
        )
        record("clean_text_option", passed, f"Clean: {len(result_clean.get('text', ''))} chars, Raw: {len(result_raw.get('text', ''))} chars")
    except Exception as e:
        record("clean_text_option", False, str(e))

    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))
