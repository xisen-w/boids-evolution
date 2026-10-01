"""
Tool Registry v1 - Phase 1.0 Implementation

Manages shared tools + personal tools with metadata and file storage.
Initializes from shared_tools_template_legacy.
Enhanced with comprehensive testing support!
"""

import os
import json
import shutil
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


class ToolRegistryV1:
    """
    Tool Registry v1 - Real tool management with initialization from template
    Enhanced with Testing Support!
    
    Now uses direct-import, typed-signature tools that return raw results.
    """
    
    def __init__(self, shared_tools_dir: str = "shared_tools", personal_tools_base_dir: str = "personal_tools"):
        self.shared_tools_dir = shared_tools_dir
        self.personal_tools_base_dir = personal_tools_base_dir
        self.template_dir = "shared_tools_template"
        
        # Initialization handled by ExperimentRunner.

    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available tools from the single, evolving shared tools directory.
        
        Returns:
            Dict of {tool_name: tool_metadata}
        """
        return self._load_shared_tools()
    
    def _load_shared_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load tools from the single shared_tools directory."""
        shared_index = os.path.join(self.shared_tools_dir, "index.json")
        
        if not os.path.exists(shared_index):
            return {}
            
        try:
            with open(shared_index, 'r') as f:
                index_data = json.load(f)
            
            tools = {}
            for tool_name, tool_data in index_data.get("tools", {}).items():
                tool_data_copy = tool_data.copy()
                tool_data_copy["tool_path"] = os.path.join(self.shared_tools_dir, tool_data["file"])
                tool_data_copy["type"] = "shared"
                
                # Complexity
                if "complexity" not in tool_data_copy:
                    try:
                        from .complexity_analyzer import TCILiteAnalyzer
                        analyzer = TCILiteAnalyzer()
                        tool_file_path = os.path.join(self.shared_tools_dir, tool_data["file"])
                        if os.path.exists(tool_file_path):
                            tool_path = Path(tool_file_path)
                            complexity = analyzer.analyze_single_tool(tool_path, {tool_path.stem})
                            if isinstance(complexity, dict):
                                tool_data_copy["complexity"] = {
                                    "tci_score": complexity.get("tci_score", 0.0),
                                    "code_complexity": complexity.get("code_complexity", 0.0),
                                    "interface_complexity": complexity.get("interface_complexity", 0.0),
                                    "compositional_complexity": complexity.get("compositional_complexity", 0.0),
                                    "lines_of_code": complexity.get("lines_of_code"),
                                    "param_count": complexity.get("param_count"),
                                    "tool_calls": complexity.get("tool_calls"),
                                    "external_imports": complexity.get("external_imports")
                                }
                    except Exception:
                        tool_data_copy["complexity"] = {
                            "tci_score": 1.0,
                            "code_complexity": 0.5,
                            "interface_complexity": 0.3,
                            "compositional_complexity": 0.2
                        }
                
                tools[tool_name] = tool_data_copy
            
            return tools
            
        except Exception as e:
            print(f"Error loading shared tools: {e}")
            return {}
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Execute a tool by name with given arguments.
        Calls execute(...) directly and returns the raw result.
        """
        # Load metadata
        all_tools = self.get_all_tools()
        if tool_name not in all_tools:
            raise RuntimeError(f"Tool {tool_name} not found")
        tool_metadata = all_tools[tool_name]
        
        # Dynamic import
        tool_file = tool_metadata["tool_path"]
        if not os.path.exists(tool_file):
            raise FileNotFoundError(f"Tool file {tool_file} not found")
        
        spec = importlib.util.spec_from_file_location(tool_name, tool_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, 'execute'):
            raise AttributeError(f"Tool {tool_name} has no execute function")
        
        # Execute and return raw result
        result = module.execute(*args, **kwargs)
        
        # Update usage count in index
        self._increment_tool_usage(tool_name)
        
        return result
    
    def _increment_tool_usage(self, tool_name: str):
        """Increment usage count for a tool in its metadata."""
        try:
            all_tools = self.get_all_tools()
            if tool_name in all_tools:
                index_path = os.path.join(self.shared_tools_dir, "index.json")
                if os.path.exists(index_path):
                    with open(index_path, 'r') as f:
                        index_data = json.load(f)
                    if tool_name in index_data.get("tools", {}):
                        index_data["tools"][tool_name]["usage_count"] = index_data["tools"][tool_name].get("usage_count", 0) + 1
                        with open(index_path, 'w') as f:
                            json.dump(index_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not update usage count for {tool_name}: {e}")
    
    def _get_tool_usage(self, tool_name: str) -> int:
        """Get current usage count for a tool."""
        try:
            all_tools = self.get_all_tools()
            if tool_name in all_tools:
                tool_metadata = all_tools[tool_name]
                if "shared" in tool_metadata.get("source", ""):
                    index_path = os.path.join(self.shared_tools_dir, "index.json")
                else:
                    tool_path = tool_metadata["tool_path"]
                    agent_dir = os.path.dirname(tool_path)
                    index_path = os.path.join(agent_dir, "index.json")
                
                if os.path.exists(index_path):
                    with open(index_path, 'r') as f:
                        index_data = json.load(f)
                    
                    return index_data.get("tools", {}).get(tool_name, {}).get("usage_count", 0)
        except Exception as e:
            print(f"Warning: Could not get usage count for {tool_name}: {e}")
        return 0
    
    def execute_test(self, tool_name: str) -> Dict[str, Any]:
        """
        Execute tests for a specific tool.
        
        Args:
            tool_name: Name of tool to test
            
        Returns:
            Test execution results
        """
        all_tools = self.get_all_tools()
        
        if tool_name not in all_tools:
            return {"error": f"Tool {tool_name} not found"}
        
        tool_metadata = all_tools[tool_name]
        
        if not tool_metadata.get("has_test"):
            return {"error": f"No test found for tool {tool_name}"}
        
        test_file = tool_metadata.get("test_path")
        
        if not test_file or not os.path.exists(test_file):
            return {"error": f"Test file not found: {test_file}"}
        
        try:
            # Execute test file
            import subprocess
            import sys
            
            # Determine working directory based on tool type
            if tool_metadata["type"] == "shared":
                cwd = self.shared_tools_dir
                relative_test_file = os.path.join("_tests", f"{tool_name}_test.py")
            else:
                agent_dir = tool_metadata.get("creator_agent")
                cwd = os.path.join(self.personal_tools_base_dir, agent_dir)
                relative_test_file = os.path.join("_tests", f"{tool_name}_test.py")
            
            result = subprocess.run(
                [sys.executable, relative_test_file],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    test_results = json.loads(result.stdout)
                except:
                    test_results = {
                        "tool_name": tool_name,
                        "execution_success": True,
                        "raw_output": result.stdout,
                        "parse_error": "Could not parse test results as JSON"
                    }
            else:
                test_results = {
                    "tool_name": tool_name,
                    "execution_success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
            
            return {"success": True, "test_results": test_results}
            
        except Exception as e:
            return {"error": f"Test execution failed: {str(e)}"}
    
    def get_shared_tools_summary(self) -> Dict[str, Any]:
        """Get summary of shared tools for agent observation."""
        shared_tools = self._load_shared_tools()
        
        summary = {
            "total_shared_tools": len(shared_tools),
            "tool_names": list(shared_tools.keys()),
            "tool_types": {},
            "tools_by_creator": {},
            "testing_summary": {
                "tools_with_tests": 0,
                "tools_with_results": 0,
                "passed_tests": 0,
                "failed_tests": 0
            }
        }
        
        for tool_name, tool_data in shared_tools.items():
            # Count by type if available
            tool_type = tool_data.get("type", "unknown")
            summary["tool_types"][tool_type] = summary["tool_types"].get(tool_type, 0) + 1
            
            # Count by creator
            creator = tool_data.get("created_by", "unknown")
            summary["tools_by_creator"][creator] = summary["tools_by_creator"].get(creator, 0) + 1
            
            # Count testing stats
            if tool_data.get("has_test"):
                summary["testing_summary"]["tools_with_tests"] += 1
            if tool_data.get("has_test_results"):
                summary["testing_summary"]["tools_with_results"] += 1
                if tool_data.get("test_passed"):
                    summary["testing_summary"]["passed_tests"] += 1
                else:
                    summary["testing_summary"]["failed_tests"] += 1
        
        return summary
    
    def get_all_tools_with_test_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all tools with their test status for comprehensive overview."""
        all_tools = self.get_all_tools()
        
        tools_with_tests = {}
        for tool_name, tool_data in all_tools.items():
            test_summary = {
                "tool_name": tool_name,
                "tool_type": tool_data.get("type", "unknown"),
                "creator": tool_data.get("created_by", tool_data.get("creator_agent", "unknown")),
                "has_test": tool_data.get("has_test", False),
                "has_results": tool_data.get("has_test_results", False),
                "test_passed": tool_data.get("test_passed"),
                "last_tested": tool_data.get("last_tested")
            }
            tools_with_tests[tool_name] = test_summary
        
        return tools_with_tests
    
    def add_shared_tool(self, tool_name: str, tool_code: str, tool_metadata: Dict[str, Any]) -> bool:
        """
        Add a new tool to shared tools directory.
        
        Args:
            tool_name: Name of the tool
            tool_code: Python code for the tool
            tool_metadata: Tool metadata (description, parameters, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            # Write tool file
            tool_file = os.path.join(self.shared_tools_dir, f"{tool_name}.py")
            with open(tool_file, 'w') as f:
                f.write(tool_code)
            
            # Update shared index
            shared_index = os.path.join(self.shared_tools_dir, "index.json")
            
            # Load existing index
            if os.path.exists(shared_index):
                with open(shared_index, 'r') as f:
                    index_data = json.load(f)
            else:
                index_data = {"tools": {}}
            
            # Add new tool to index
            tool_metadata_copy = tool_metadata.copy()
            tool_metadata_copy["file"] = f"{tool_name}.py"
            
            index_data["tools"][tool_name] = tool_metadata_copy
            
            # Save updated index
            with open(shared_index, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            print(f"✅ Added shared tool: {tool_name}")
            return True
            
        except Exception as e:
            print(f"Error adding shared tool {tool_name}: {e}")
            return False


def initialize_tool_system() -> ToolRegistryV1:
    """
    Initialize the complete tool system with testing support.
    
    Returns:
        ToolRegistryV1: Initialized tool registry
    """
    print("🔧 Initializing Tool System v1 with Testing Support")
    print("=" * 60)
    
    # Create tool registry
    registry = ToolRegistryV1()
    
    # Get summary
    summary = registry.get_shared_tools_summary()
    print(f"📊 Tool System Summary:")
    print(f"   Shared tools: {summary['total_shared_tools']}")
    print(f"   Available tools: {summary['tool_names']}")
    print(f"   Tool types: {summary['tool_types']}")
    print(f"   Creators: {summary['tools_by_creator']}")
    
    # Testing summary
    testing = summary['testing_summary']
    print(f"🧪 Testing Summary:")
    print(f"   Tools with tests: {testing['tools_with_tests']}")
    print(f"   Tools with results: {testing['tools_with_results']}")
    print(f"   Passed tests: {testing['passed_tests']}")
    print(f"   Failed tests: {testing['failed_tests']}")
    
    # Test tool execution
    all_tools = registry.get_all_tools()
    # Remove calculate demo execution which may not exist anymore
    # (left intentionally blank)
    
    print(f"\n✅ Tool System v1 with Testing initialized!")
    return registry


def main():
    """Test the Tool Registry v1 with testing capabilities."""
    registry = initialize_tool_system()
    
    print(f"\n📋 All Available Tools with Test Status:")
    tools_with_tests = registry.get_all_tools_with_test_status()
    
    for tool_name, tool_info in tools_with_tests.items():
        test_status = "✅ TESTED" if tool_info["test_passed"] else ("❌ FAILED" if tool_info["has_results"] else ("🔧 HAS TEST" if tool_info["has_test"] else "⚠️  NO TEST"))
        creator = tool_info["creator"]
        tool_type = tool_info["tool_type"]
        
        print(f"   🔧 {tool_name} ({tool_type}) by {creator} - {test_status}")
        if tool_info["last_tested"]:
            print(f"      Last tested: {tool_info['last_tested']}")


if __name__ == "__main__":
    main() 
