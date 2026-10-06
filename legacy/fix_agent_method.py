#!/usr/bin/env python3
"""
Fix the missing _update_tool_index method in agent_v1.py
"""

def fix_agent_method():
    with open('src/agent_v1.py', 'r') as f:
        content = f.read()
    
    # Find where to add the method (after _analyze_tool_complexity method)
    method_end = content.find("def _extract_tool_name(self, tool_design: str) -> str:")
    if method_end == -1:
        print("❌ Could not find insertion point")
        return
    
    # Add the missing _update_tool_index method
    update_tool_index_method = '''
    def _update_tool_index(self, tool_name: str, tool_design: str, round_num: int, complexity_data: Dict = None) -> Dict[str, Any]:
        """Update the agent's tool index with new tool (including complexity)."""
        
        tool_metadata = {
            "name": tool_name,
            "description": tool_design,
            "file": f"{tool_name}.py",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat(),
            "created_in_round": round_num,
            "adoption_count": 0,
            "has_test": False,
            "test_file": f"_tests/{tool_name}_test.py",
            "test_results_file": f"_testResults/{tool_name}_results.json",
            "test_passed": None,
            "last_tested": None,
            "test_execution_success": None,
            "complexity": complexity_data or {}  # 🆕 NEW: Add complexity data
        }
        
        # Update the index.json file
        index_file = os.path.join(self.personal_tool_dir, "index.json")
        
        # Load existing index or create new one
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
            except:
                index_data = {"tools": {}}
        else:
            index_data = {"tools": {}}
        
        # Add the tool to the index
        index_data["tools"][tool_name] = tool_metadata
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        return tool_metadata

    '''
    
    # Insert the method
    content = content[:method_end] + update_tool_index_method + "    " + content[method_end:]
    
    # Write the updated content
    with open('src/agent_v1.py', 'w') as f:
        f.write(content)
    
    print("✅ Added missing _update_tool_index method to agent_v1.py")

if __name__ == "__main__":
    fix_agent_method()
