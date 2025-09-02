import sys
import os
import json
from datetime import datetime
import tempfile
import shutil

def run_tests():
    """Run comprehensive tests for file_write tool"""
    results = {
        "tool_name": "file_write",
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
        import file_write
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    
    try:
        test_cases = [
            {"name": "test_write_with_filename", "params": {"filename": "test1.txt", "content": "Hello World"}, "check_file": "test1.txt"},
            {"name": "test_write_without_filename", "params": {"content": "Auto filename test"}, "check_file": None},  # Will be auto-generated
            {"name": "test_write_empty_content", "params": {"filename": "empty.txt", "content": ""}, "check_file": "empty.txt"},
            {"name": "test_write_multiline", "params": {"filename": "multi.txt", "content": "Line 1\nLine 2\nLine 3"}, "check_file": "multi.txt"},
            {"name": "test_write_special_chars", "params": {"filename": "special.txt", "content": "Special: !@#$%^&*()"}, "check_file": "special.txt"},
        ]
        
        # Change to test directory
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        for test_case in test_cases:
            results["total_tests"] += 1
            try:
                result = file_write.execute(test_case["params"])
                
                passed = result.get("success", False)
                
                # Additional check: verify file was created
                if passed and test_case["check_file"]:
                    file_path = os.path.join("agent_outputs", test_case["check_file"])
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read()
                        passed = passed and (content == test_case["params"]["content"])
                    else:
                        passed = False
                elif passed and not test_case["check_file"]:
                    # Check that some file was created in agent_outputs
                    outputs_dir = "agent_outputs"
                    if os.path.exists(outputs_dir):
                        files = os.listdir(outputs_dir)
                        passed = len(files) > 0
                    else:
                        passed = False
                
                # Clean result by removing outdated energy_gain
                clean_result = {k: v for k, v in result.items() if k != "energy_gain"}
                
                results["tests"].append({
                    "name": test_case["name"],
                    "passed": passed,
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
        
        os.chdir(original_cwd)
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir, ignore_errors=True)
    
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))
