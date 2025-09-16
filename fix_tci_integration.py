#!/usr/bin/env python3
"""
Fix TCI integration in the experiment analyzer
"""

def fix_tci_integration():
    with open('experiment_result_analyzer.py', 'r') as f:
        content = f.read()
    
    # Find and replace the TCI analysis section
    old_tci_code = """            # TCI Analysis using our complexity analyzer
            try:
                # Create a temporary directory structure for TCI analysis
                temp_dir = tool_file.parent
                tci_results = self.tci_analyzer.analyze_tools_directory(str(temp_dir))
                
                tool_tci = tci_results.get(agent_id, {}).get(metrics.name, {})
                if tool_tci:
                    metrics.tci_score = tool_tci.get('tci_score', 0.0)
                    metrics.code_complexity = tool_tci.get('code_complexity', 0.0)
                    metrics.interface_complexity = tool_tci.get('interface_complexity', 0.0)
                    metrics.compositional_complexity = tool_tci.get('compositional_complexity', 0.0)
            
            except Exception as e:
                print(f"⚠️ TCI analysis failed for {metrics.name}: {e}")"""
    
    new_tci_code = """            # TCI Analysis using our complexity analyzer
            try:
                # Analyze the specific tool directory
                temp_dir = tool_file.parent
                tci_results = self.tci_analyzer.analyze_tools_directory(str(temp_dir))
                
                # TCI results are keyed by tool filename, not agent_id
                tool_filename = tool_file.stem  # Get filename without extension
                tool_tci = tci_results.get(tool_filename, {})
                
                if tool_tci and isinstance(tool_tci, dict):
                    metrics.tci_score = tool_tci.get('tci_score', 0.0)
                    metrics.code_complexity = tool_tci.get('code_complexity', 0.0)
                    metrics.interface_complexity = tool_tci.get('interface_complexity', 0.0)
                    metrics.compositional_complexity = tool_tci.get('compositional_complexity', 0.0)
                    # Also get the lines_of_code from TCI if available
                    if metrics.lines_of_code == 0:
                        metrics.lines_of_code = tool_tci.get('lines_of_code', 0)
            
            except Exception as e:
                print(f"⚠️ TCI analysis failed for {metrics.name}: {e}")"""
    
    # Replace the code
    content = content.replace(old_tci_code, new_tci_code)
    
    # Write back
    with open('experiment_result_analyzer.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed TCI integration - now using correct tool filename keys")

if __name__ == "__main__":
    fix_tci_integration()
