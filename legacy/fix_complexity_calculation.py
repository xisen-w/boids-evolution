#!/usr/bin/env python3
"""
Fix the system complexity calculation to work with actual tool data
"""

def fix_complexity_calculation():
    with open('run_experiment.py', 'r') as f:
        content = f.read()
    
    # Replace the problematic tool registry approach with direct file-based approach
    old_complexity_method = '''    def _calculate_and_record_system_complexity(self, round_num: int):
        """Calculate the average TCI of all tools in the system at the end of a round."""
        all_tools_metadata = self.tool_registry.get_all_tools()
        total_tci = 0
        total_code_complexity = 0
        total_interface_complexity = 0
        total_compositional_complexity = 0
        tool_count = 0
        
        for tool_name, metadata in all_tools_metadata.items():
            complexity_data = metadata.get("complexity")
            if complexity_data and "tci_score" in complexity_data:
                total_tci += complexity_data.get("tci_score", 0)
                total_code_complexity += complexity_data.get("code_complexity", 0)
                total_interface_complexity += complexity_data.get("interface_complexity", 0)
                total_compositional_complexity += complexity_data.get("compositional_complexity", 0)
                tool_count += 1
        
        average_tci = total_tci / tool_count if tool_count > 0 else 0
        avg_code = total_code_complexity / tool_count if tool_count > 0 else 0
        avg_interface = total_interface_complexity / tool_count if tool_count > 0 else 0
        avg_compositional = total_compositional_complexity / tool_count if tool_count > 0 else 0

        self.complexity_over_rounds.append({
            "round": round_num,
            "average_tci": average_tci,
            "avg_code_complexity": avg_code,
            "avg_interface_complexity": avg_interface,
            "avg_compositional_complexity": avg_compositional,
            "tool_count": tool_count
        })
        logger.info(f"   📈 System Complexity: Avg TCI = {average_tci:.2f} across {tool_count} tools.")'''
    
    new_complexity_method = '''    def _calculate_and_record_system_complexity(self, round_num: int):
        """Calculate the average TCI of all tools in the system at the end of a round."""
        total_tci = 0
        total_code_complexity = 0
        total_interface_complexity = 0
        total_compositional_complexity = 0
        tool_count = 0
        
        # Collect complexity data from all agent tools
        for agent in self.agents:
            for tool_name, tool_metadata in agent.self_built_tools.items():
                complexity_data = tool_metadata.get("complexity", {})
                if complexity_data and complexity_data.get("tci_score", 0) > 0:
                    total_tci += complexity_data.get("tci_score", 0)
                    total_code_complexity += complexity_data.get("code_complexity", 0)
                    total_interface_complexity += complexity_data.get("interface_complexity", 0)
                    total_compositional_complexity += complexity_data.get("compositional_complexity", 0)
                    tool_count += 1
        
        # Also check shared tools if they exist
        shared_index_file = os.path.join(self.shared_tools_dir, "index.json")
        if os.path.exists(shared_index_file):
            shared_index_data = self._load_index_json(shared_index_file)
            for tool_name, tool_metadata in shared_index_data.get("tools", {}).items():
                complexity_data = tool_metadata.get("complexity", {})
                if complexity_data and complexity_data.get("tci_score", 0) > 0:
                    total_tci += complexity_data.get("tci_score", 0)
                    total_code_complexity += complexity_data.get("code_complexity", 0)
                    total_interface_complexity += complexity_data.get("interface_complexity", 0)
                    total_compositional_complexity += complexity_data.get("compositional_complexity", 0)
                    tool_count += 1
        
        average_tci = total_tci / tool_count if tool_count > 0 else 0
        avg_code = total_code_complexity / tool_count if tool_count > 0 else 0
        avg_interface = total_interface_complexity / tool_count if tool_count > 0 else 0
        avg_compositional = total_compositional_complexity / tool_count if tool_count > 0 else 0

        self.complexity_over_rounds.append({
            "round": round_num,
            "average_tci": average_tci,
            "avg_code_complexity": avg_code,
            "avg_interface_complexity": avg_interface,
            "avg_compositional_complexity": avg_compositional,
            "tool_count": tool_count
        })
        logger.info(f"   📈 System Complexity: Avg TCI = {average_tci:.2f} across {tool_count} tools.")'''
    
    content = content.replace(old_complexity_method, new_complexity_method)
    
    with open('run_experiment.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed system complexity calculation to work with agent tool data")

if __name__ == "__main__":
    fix_complexity_calculation()
