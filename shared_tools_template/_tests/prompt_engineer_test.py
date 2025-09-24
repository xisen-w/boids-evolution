import sys
import os
import json
from datetime import datetime

def run_tests():
    """Run all tests for prompt_engineer"""
    results = {
        "tool_name": "prompt_engineer",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Import the tool
    try:
        import importlib.util
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        tool_file = os.path.join(parent_dir, "prompt_engineer.py")
        spec = importlib.util.spec_from_file_location("prompt_engineer", tool_file)
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)
        prompt_engineer = tool_module.execute
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
    
    # Mock context for testing
    class MockContext:
        def call_tool(self, tool_name, params):
            if tool_name == 'ai_text_generate':
                return {
                    'success': True,
                    'result': 'This is a mock AI-generated response for testing purposes.'
                }
            return {'success': False, 'error': f'Tool {tool_name} not found'}
    
    context = MockContext()
    
    # Test 1: Basic functionality with context
    try:
        result = prompt_engineer({
            'task': 'Analyze the structure of a sonnet',
            'domain': 'poetry',
            'style': 'analytical'
        }, context)
        
        if result and 'success' in result and result['success']:
            if 'result' in result and 'prompt_techniques_used' in result:
                record_result("Basic functionality with context", True)
            else:
                record_result("Basic functionality with context", False, "Missing expected result fields")
        else:
            record_result("Basic functionality with context", False, f"Unexpected result: {result}")
    except Exception as e:
        record_result("Basic functionality with context", False, str(e))
    
    # Test 2: Error handling without context
    try:
        result = prompt_engineer({
            'task': 'Test task'
        }, None)
        
        if result and 'error' in result and 'No context provided' in result['error']:
            record_result("Error handling without context", True)
        else:
            record_result("Error handling without context", False, f"Expected error for missing context, got: {result}")
    except Exception as e:
        record_result("Error handling without context", False, str(e))
    
    # Test 3: Error handling with missing task
    try:
        result = prompt_engineer({}, context)
        
        if result and 'error' in result and 'No task provided' in result['error']:
            record_result("Error handling with missing task", True)
        else:
            record_result("Error handling with missing task", False, f"Expected error for missing task, got: {result}")
    except Exception as e:
        record_result("Error handling with missing task", False, str(e))
    
    # Test 4: Few-shot learning functionality
    try:
        examples = [
            {'input': 'What is a metaphor?', 'output': 'A metaphor is a figure of speech that compares two things without using "like" or "as".'},
            {'input': 'What is alliteration?', 'output': 'Alliteration is the repetition of consonant sounds at the beginning of words.'}
        ]
        
        result = prompt_engineer({
            'task': 'Explain poetic devices',
            'domain': 'poetry',
            'examples': examples
        }, context)
        
        if result and 'success' in result and result['success']:
            if 'few_shot_learning' in result.get('prompt_techniques_used', []):
                record_result("Few-shot learning functionality", True)
            else:
                record_result("Few-shot learning functionality", False, "Few-shot learning not detected in techniques")
        else:
            record_result("Few-shot learning functionality", False, f"Unexpected result: {result}")
    except Exception as e:
        record_result("Few-shot learning functionality", False, str(e))
    
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))
