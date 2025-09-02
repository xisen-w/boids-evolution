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
from typing import Dict, List, Any, Optional


class ToolRegistryV1:
    """
    Tool Registry v1 - Real tool management with initialization from template
    Enhanced with Testing Support!
    
    Features:
    - Initialize shared tools from shared_tools_template_legacy
    - Manage personal tools from all agents
    - Dynamic tool loading and execution
    - Tool metadata with JSON index files
    - Comprehensive testing infrastructure with _tests and _testResults folders
    """
    
    def __init__(self, shared_tools_dir: str = "shared_tools", personal_tools_base_dir: str = "personal_tools"):
        self.shared_tools_dir = shared_tools_dir
        self.personal_tools_base_dir = personal_tools_base_dir
        self.template_dir = "shared_tools_template"
        
        # Initialize shared tools from template if needed
        self._initialize_shared_tools()
        
        # Create testing infrastructure
        self._initialize_testing_infrastructure()
        
        # FIX: Add test status to shared tools
        self._update_shared_tools_with_test_status()
        
    def _initialize_shared_tools(self):
        """Initialize shared tools directory from template."""
        
        # Create shared tools directory
        os.makedirs(self.shared_tools_dir, exist_ok=True)
        
        # Check if already initialized (has index.json)
        shared_index = os.path.join(self.shared_tools_dir, "index.json")
        
        if os.path.exists(shared_index):
            print(f"📂 Shared tools already initialized in {self.shared_tools_dir}")
            return
            
        # Copy from template if template exists
        if os.path.exists(self.template_dir):
            print(f"🔧 Initializing shared tools from {self.template_dir}")
            
            # Copy all files from template
            for item in os.listdir(self.template_dir):
                if item == "__pycache__":
                    continue
                    
                source_path = os.path.join(self.template_dir, item)
                dest_path = os.path.join(self.shared_tools_dir, item)
                
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, dest_path)
                    print(f"   ✅ Copied {item}")
                    
            print(f"🎯 Shared tools initialized with {len(os.listdir(self.shared_tools_dir))-1} tools")
            
        else:
            print(f"⚠️  Template directory {self.template_dir} not found, creating empty shared tools")
            # Create empty index
            empty_index = {"tools": {}}
            with open(shared_index, 'w') as f:
                json.dump(empty_index, f, indent=2)
    
    def _initialize_testing_infrastructure(self):
        """Initialize testing directories for shared tools."""
        
        # Create testing directories for shared tools
        shared_tests_dir = os.path.join(self.shared_tools_dir, "_tests")
        shared_test_results_dir = os.path.join(self.shared_tools_dir, "_testResults")
        
        os.makedirs(shared_tests_dir, exist_ok=True)
        os.makedirs(shared_test_results_dir, exist_ok=True)
        
        print(f"🧪 Testing infrastructure initialized:")
        print(f"   Shared tests: {shared_tests_dir}")
        print(f"   Shared test results: {shared_test_results_dir}")
    
    def _update_shared_tools_with_test_status(self):
        """Add test status fields to existing shared tools."""
        shared_index = os.path.join(self.shared_tools_dir, "index.json")
        
        if not os.path.exists(shared_index):
            return
        
        try:
            with open(shared_index, 'r') as f:
                index_data = json.load(f)
            
            updated = False
            for tool_name, tool_data in index_data.get("tools", {}).items():
                # Check if test status fields are missing
                if "has_test" not in tool_data:
                    # Add test status fields to shared tools
                    tool_data["has_test"] = False
                    tool_data["test_file"] = f"_tests/{tool_name}_test.py"
                    tool_data["test_results_file"] = f"_testResults/{tool_name}_results.json"
                    tool_data["test_passed"] = None
                    tool_data["last_tested"] = None
                    tool_data["test_execution_success"] = None
                    updated = True
            
            if updated:
                # Save updated index
                with open(shared_index, 'w') as f:
                    json.dump(index_data, f, indent=2)
                print(f"✅ Added test status fields to shared tools")
                
        except Exception as e:
            print(f"⚠️  Error updating shared tools with test status: {e}")
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available tools (shared + all personal tools).
        
        Returns:
            Dict of {tool_name: tool_metadata}
        """
        all_tools = {}
        
        # Load shared tools
        shared_tools = self._load_shared_tools()
        all_tools.update(shared_tools)
        
        # Load personal tools from all agents
        personal_tools = self._load_all_personal_tools()
        all_tools.update(personal_tools)
        
        return all_tools
    
    def _load_shared_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load tools from shared_tools directory."""
        shared_index = os.path.join(self.shared_tools_dir, "index.json")
        
        if not os.path.exists(shared_index):
            return {}
            
        try:
            with open(shared_index, 'r') as f:
                index_data = json.load(f)
            
            # Add file paths to tool metadata
            tools = {}
            for tool_name, tool_data in index_data.get("tools", {}).items():
                tool_data_copy = tool_data.copy()
                tool_data_copy["tool_path"] = os.path.join(self.shared_tools_dir, tool_data["file"])
                tool_data_copy["type"] = "shared"
                
                # Add test information
                test_info = self._get_tool_test_info(tool_name, "shared")
                tool_data_copy.update(test_info)
                
                tools[tool_name] = tool_data_copy
            
            return tools
            
        except Exception as e:
            print(f"Error loading shared tools: {e}")
            return {}
    
    def _load_all_personal_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load personal tools from all agent directories."""
        all_personal_tools = {}
        
        if not os.path.exists(self.personal_tools_base_dir):
            return all_personal_tools
        
        # Iterate through agent directories
        for agent_dir in os.listdir(self.personal_tools_base_dir):
            agent_path = os.path.join(self.personal_tools_base_dir, agent_dir)
            
            if not os.path.isdir(agent_path):
                continue
                
            index_file = os.path.join(agent_path, "index.json")
            
            if not os.path.exists(index_file):
                continue
            
            try:
                with open(index_file, 'r') as f:
                    agent_index = json.load(f)
                
                # Add agent prefix to tool names to avoid conflicts
                for tool_name, tool_data in agent_index.get("tools", {}).items():
                    prefixed_name = f"{agent_dir}_{tool_name}"
                    tool_data_copy = tool_data.copy()
                    tool_data_copy["original_name"] = tool_name
                    tool_data_copy["creator_agent"] = agent_dir
                    tool_data_copy["tool_path"] = os.path.join(agent_path, tool_data["file"])
                    tool_data_copy["type"] = "personal"
                    
                    # Add test information
                    test_info = self._get_tool_test_info(tool_name, "personal", agent_dir)
                    tool_data_copy.update(test_info)
                    
                    all_personal_tools[prefixed_name] = tool_data_copy
                    
            except Exception as e:
                print(f"Error loading tools from {agent_dir}: {e}")
                continue
        
        return all_personal_tools
    
    def _get_tool_test_info(self, tool_name: str, tool_type: str, agent_dir: str = None) -> Dict[str, Any]:
        """Get test information for a tool."""
        test_info = {
            "has_test": False,
            "has_test_results": False,
            "test_path": None,
            "test_results_path": None,
            "last_tested": None,
            "test_passed": None
        }
        
        if tool_type == "shared":
            tests_dir = os.path.join(self.shared_tools_dir, "_tests")
            results_dir = os.path.join(self.shared_tools_dir, "_testResults")
        elif tool_type == "personal" and agent_dir:
            agent_path = os.path.join(self.personal_tools_base_dir, agent_dir)
            tests_dir = os.path.join(agent_path, "_tests")
            results_dir = os.path.join(agent_path, "_testResults")
        else:
            return test_info
        
        # Check for test file
        test_file = os.path.join(tests_dir, f"{tool_name}_test.py")
        if os.path.exists(test_file):
            test_info["has_test"] = True
            test_info["test_path"] = test_file
        
        # Check for test results
        results_file = os.path.join(results_dir, f"{tool_name}_results.json")
        if os.path.exists(results_file):
            test_info["has_test_results"] = True
            test_info["test_results_path"] = results_file
            
            # Load test results
            try:
                with open(results_file, 'r') as f:
                    results = json.load(f)
                test_info["last_tested"] = results.get("timestamp")
                test_info["test_passed"] = results.get("all_passed", False)
            except:
                pass
        
        return test_info
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Parameters to pass to tool
            
        Returns:
            Tool execution result
        """
        all_tools = self.get_all_tools()
        
        if tool_name not in all_tools:
            return {"error": f"Tool {tool_name} not found"}
        
        tool_metadata = all_tools[tool_name]
        
        try:
            # Get tool file path
            tool_file = tool_metadata["tool_path"]
            
            if not os.path.exists(tool_file):
                return {"error": f"Tool file {tool_file} not found"}
            
            # Dynamic import and execution
            spec = importlib.util.spec_from_file_location(tool_name, tool_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Execute the tool
            if hasattr(module, 'execute'):
                result = module.execute(parameters)
                return {"success": True, "result": result, "tool_name": tool_name}
            else:
                return {"error": f"Tool {tool_name} has no execute function"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
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
    if "calculate" in all_tools:
        print(f"\n🧪 Testing calculate tool:")
        test_result = registry.execute_tool("calculate", {
            "operation": "add",
            "a": 5,
            "b": 3
        })
        print(f"   Result: {test_result}")
    
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