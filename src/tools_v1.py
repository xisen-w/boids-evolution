"""
Tool Registry v1 - Phase 1.0 Implementation

Manages shared tools + personal tools with metadata and file storage.
Initializes from shared_tools_template_legacy.
"""

import os
import json
import shutil
import importlib.util
from typing import Dict, List, Any, Optional


class ToolRegistryV1:
    """
    Tool Registry v1 - Real tool management with initialization from template
    
    Features:
    - Initialize shared tools from shared_tools_template_legacy
    - Manage personal tools from all agents
    - Dynamic tool loading and execution
    - Tool metadata with JSON index files
    """
    
    def __init__(self, shared_tools_dir: str = "shared_tools"):
        self.shared_tools_dir = shared_tools_dir
        self.personal_tools_base_dir = "personal_tools"
        self.template_dir = "shared_tools_template_legacy"
        
        # Initialize shared tools from template if needed
        self._initialize_shared_tools()
        
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
                    
                    all_personal_tools[prefixed_name] = tool_data_copy
                    
            except Exception as e:
                print(f"Error loading tools from {agent_dir}: {e}")
                continue
        
        return all_personal_tools
    
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
    
    def get_shared_tools_summary(self) -> Dict[str, Any]:
        """Get summary of shared tools for agent observation."""
        shared_tools = self._load_shared_tools()
        
        summary = {
            "total_shared_tools": len(shared_tools),
            "tool_names": list(shared_tools.keys()),
            "tool_types": {},
            "tools_by_creator": {}
        }
        
        for tool_name, tool_data in shared_tools.items():
            # Count by type if available
            tool_type = tool_data.get("type", "unknown")
            summary["tool_types"][tool_type] = summary["tool_types"].get(tool_type, 0) + 1
            
            # Count by creator
            creator = tool_data.get("created_by", "unknown")
            summary["tools_by_creator"][creator] = summary["tools_by_creator"].get(creator, 0) + 1
        
        return summary
    
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
    Initialize the complete tool system.
    
    Returns:
        ToolRegistryV1: Initialized tool registry
    """
    print("🔧 Initializing Tool System v1")
    print("=" * 50)
    
    # Create tool registry
    registry = ToolRegistryV1()
    
    # Get summary
    summary = registry.get_shared_tools_summary()
    print(f"📊 Tool System Summary:")
    print(f"   Shared tools: {summary['total_shared_tools']}")
    print(f"   Available tools: {summary['tool_names']}")
    print(f"   Tool types: {summary['tool_types']}")
    print(f"   Creators: {summary['tools_by_creator']}")
    
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
    
    print(f"\n✅ Tool System v1 initialized!")
    return registry


def main():
    """Test the Tool Registry v1."""
    registry = initialize_tool_system()
    
    print(f"\n📋 All Available Tools:")
    all_tools = registry.get_all_tools()
    
    for tool_name, tool_data in all_tools.items():
        tool_type = tool_data.get("type", "unknown")
        creator = tool_data.get("created_by", "unknown")
        description = tool_data.get("description", "No description")[:50]
        print(f"   🔧 {tool_name} ({tool_type}) by {creator}")
        print(f"      {description}...")


if __name__ == "__main__":
    main() 