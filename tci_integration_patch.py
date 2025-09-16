#!/usr/bin/env python3
"""
Apply TCI integration patch to agent_v1.py
"""

def apply_tci_patch():
    with open('src/agent_v1.py', 'r') as f:
        content = f.read()
    
    # 1. Add TCI analyzer import at the top
    import_section = """import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime"""
    
    new_import_section = """import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime"""
    
    content = content.replace(import_section, new_import_section)
    
    # 2. Add TCI analysis method after _create_tool_file method
    tci_method = '''
    def _analyze_tool_complexity(self, tool_file: str, tool_name: str) -> Dict[str, Any]:
        """Analyze tool for TCI complexity immediately after creation."""
        try:
            # Import TCI analyzer
            from src.complexity_analyzer import TCILiteAnalyzer
            
            analyzer = TCILiteAnalyzer()
            
            # Analyze the specific tool file directory
            tool_dir = os.path.dirname(tool_file)
            results = analyzer.analyze_tools_directory(tool_dir)
            
            # Extract TCI data for this specific tool
            tool_filename = os.path.splitext(os.path.basename(tool_file))[0]
            tci_data = results.get(tool_filename, {})
            
            if tci_data and isinstance(tci_data, dict):
                complexity_data = {
                    "tci_score": tci_data.get("tci_score", 0.0),
                    "code_complexity": tci_data.get("code_complexity", 0.0),
                    "interface_complexity": tci_data.get("interface_complexity", 0.0),
                    "compositional_complexity": tci_data.get("compositional_complexity", 0.0),
                    "lines_of_code": tci_data.get("lines_of_code", 0),
                    "param_count": tci_data.get("param_count", 0),
                    "tool_calls": tci_data.get("tool_calls", 0),
                    "external_imports": tci_data.get("external_imports", 0)
                }
                print(f"   📊 TCI Analysis: {tool_name} = {complexity_data['tci_score']:.2f}")
                return complexity_data
            else:
                print(f"   ⚠️ TCI Analysis: No data for {tool_name}")
                return {"tci_score": 0.0, "code_complexity": 0.0, "interface_complexity": 0.0, "compositional_complexity": 0.0}
                
        except Exception as e:
            print(f"   ❌ TCI analysis failed for {tool_name}: {e}")
            return {"tci_score": 0.0, "code_complexity": 0.0, "interface_complexity": 0.0, "compositional_complexity": 0.0}
'''
    
    # Find where to insert the method (after _create_tool_file method)
    method_end = content.find("def _extract_tool_name(self, tool_design: str) -> str:")
    if method_end != -1:
        content = content[:method_end] + tci_method + "\n    " + content[method_end:]
    
    # 3. Update _create_tool_file to use TCI analysis
    old_create_tool = '''            # Update personal tool index
            tool_metadata = self._update_tool_index(tool_name, tool_design, round_num)'''
    
    new_create_tool = '''            # 🆕 NEW: Analyze tool for TCI complexity
            complexity_data = self._analyze_tool_complexity(tool_file, tool_name)
            
            # Update personal tool index (with complexity data)
            tool_metadata = self._update_tool_index(tool_name, tool_design, round_num, complexity_data)'''
    
    content = content.replace(old_create_tool, new_create_tool)
    
    # 4. Update _update_tool_index method signature and implementation
    old_update_signature = "def _update_tool_index(self, tool_name: str, tool_design: str, round_num: int) -> Dict[str, Any]:"
    new_update_signature = "def _update_tool_index(self, tool_name: str, tool_design: str, round_num: int, complexity_data: Dict = None) -> Dict[str, Any]:"
    
    content = content.replace(old_update_signature, new_update_signature)
    
    # Find the tool_metadata dict in _update_tool_index and add complexity field
    old_metadata_end = '''            "test_passed": None,
            "last_tested": None,
            "test_execution_success": None
        }'''
    
    new_metadata_end = '''            "test_passed": None,
            "last_tested": None,
            "test_execution_success": None,
            "complexity": complexity_data or {}  # 🆕 NEW: Add complexity data
        }'''
    
    content = content.replace(old_metadata_end, new_metadata_end)
    
    # Write the updated content
    with open('src/agent_v1.py', 'w') as f:
        f.write(content)
    
    print("✅ Applied TCI integration patch to agent_v1.py")

if __name__ == "__main__":
    apply_tci_patch()
