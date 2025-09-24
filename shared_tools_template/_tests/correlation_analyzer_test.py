#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import correlation_analyzer

def record(results, test_name, passed, expected=None, actual=None):
    results["tests"].append({
        "name": test_name,
        "passed": bool(passed),
        **({"expected": expected, "actual": actual} if expected is not None else {})
    })
    if passed:
        results["passed_tests"] += 1
    else:
        results["failed_tests"] += 1

def test_correlation_analyzer():
    results = {
        "tool_name": "correlation_analyzer",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }
    
    # Test 1: Basic correlation with sample data
    try:
        sample_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [2, 4, 6, 8, 10],  # Perfect positive correlation with A
            'C': [5, 4, 3, 2, 1],   # Perfect negative correlation with A
            'D': ['x', 'y', 'z', 'w', 'v']  # Non-numeric column
        })
        
        result = correlation_analyzer.execute(sample_data)
        
        # Should return 3x3 matrix (A, B, C - excluding non-numeric D)
        expected_shape = (3, 3)
        actual_shape = result.shape
        
        # Check correlation values
        corr_AB = result.loc['A', 'B']  # Should be 1.0 (perfect positive)
        corr_AC = result.loc['A', 'C']  # Should be -1.0 (perfect negative)
        
        passed = (actual_shape == expected_shape and 
                 abs(corr_AB - 1.0) < 0.001 and 
                 abs(corr_AC - (-1.0)) < 0.001)
        
        record(results, "basic_correlation", passed)
        
    except Exception as e:
        record(results, "basic_correlation", False)
        print(f"Test basic_correlation failed: {e}")
    
    # Test 2: Specific columns selection
    try:
        result = correlation_analyzer.execute(sample_data, columns=['A', 'B'])
        expected_shape = (2, 2)
        actual_shape = result.shape
        
        passed = actual_shape == expected_shape
        record(results, "column_selection", passed)
        
    except Exception as e:
        record(results, "column_selection", False)
        print(f"Test column_selection failed: {e}")
    
    # Test 3: Different correlation method
    try:
        result = correlation_analyzer.execute(sample_data, method='spearman')
        passed = isinstance(result, pd.DataFrame) and result.shape == (3, 3)
        record(results, "spearman_method", passed)
        
    except Exception as e:
        record(results, "spearman_method", False)
        print(f"Test spearman_method failed: {e}")
    
    # Finalize results
    results["total_tests"] = len(results["tests"])
    results["all_passed"] = results["failed_tests"] == 0
    
    return results

if __name__ == "__main__":
    results = test_correlation_analyzer()
    print(json.dumps(results, indent=2))
    
    # Save results to file
    os.makedirs("_testResults", exist_ok=True)
    with open("_testResults/correlation_analyzer_results.json", "w") as f:
        json.dump(results, f, indent=2)
