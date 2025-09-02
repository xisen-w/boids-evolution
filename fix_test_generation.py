#!/usr/bin/env python3
"""
Fix the test generation prompt in agent_v1.py
"""

import re

def fix_agent_file():
    with open('src/agent_v1.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace the test generation prompt section
    old_section = '''    # Test cases here...
    
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))"""

        user_prompt = f"""Create comprehensive tests for {tool_name}.
Generate at least 3-5 different test cases covering:
- Normal usage
- Edge cases  
- Error conditions
- Parameter validation

Output ONLY the Python test code."""'''
    
    new_section = '''    def record_result(test_name, passed, error_msg=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({{
            "test_name": test_name,
            "passed": passed,
            "error": error_msg
        }})
    
    # CRITICAL: Tools expect parameters as a dictionary!
    # CORRECT: result = {tool_name}.execute({{'param1': value1, 'param2': value2}})
    # WRONG: result = {tool_name}.execute(value1, value2)
    
    # Example test case:
    try:
        # Call tool with parameters dictionary
        result = {tool_name}.execute({{'test_param': 'test_value'}})
        if result.get('success'):
            record_result("Basic functionality", True)
        else:
            record_result("Basic functionality", False, result.get('error', 'Unknown error'))
    except Exception as e:
        record_result("Basic functionality", False, str(e))
    
    # Add more test cases following the same pattern...
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))"""

        user_prompt = f"""Create comprehensive tests for {tool_name}.

CRITICAL: Tools use this calling convention:
- result = {tool_name}.execute({{'param1': value1, 'param2': value2}})
- NOT: result = {tool_name}.execute(value1, value2)

Generate at least 5-8 different test cases covering:
- Normal usage with correct parameter dictionaries
- Edge cases with boundary values
- Error conditions and invalid inputs
- Parameter validation and missing parameters

Each test should:
1. Call the tool with proper parameter dictionary format
2. Check result.get('success') for success/failure
3. Use record_result() to track test outcomes

Output ONLY the Python test code."""'''
    
    # Replace the section
    content = content.replace(old_section, new_section)
    
    # Write back
    with open('src/agent_v1.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed test generation prompt in agent_v1.py")
    print("�� Now tests will call tools with correct parameter dictionaries!")

if __name__ == "__main__":
    fix_agent_file()
