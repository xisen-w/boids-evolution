"""
Enhanced Tool Registry - Manages shared and personal tools for agents.
Supports dynamic loading from filesystem directories.
"""
import json
import os
import importlib.util
from typing import Dict, Any, Optional, List
from datetime import datetime


class EnhancedToolRegistry:
    """Enhanced registry for managing shared and personal tools."""
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id
        self.shared_tools_dir = "shared_tools"
        self.personal_tools_dir = "personal_tools"
        self.shared_tools = {}
        self.personal_tools = {}
        self._load_all_tools()
    
    def _load_all_tools(self):
        """Load all tools from shared and personal directories."""
        self._load_shared_tools()
        if self.agent_id:
            self._load_personal_tools()
    
    def _load_shared_tools(self):
        """Load tools from the shared_tools directory."""
        index_path = os.path.join(self.shared_tools_dir, "index.json")
        
        if not os.path.exists(index_path):
            print(f"Warning: No shared tools index found at {index_path}")
            return
        
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            for tool_name, tool_info in index_data.get('tools', {}).items():
                tool_file = tool_info.get('file')
                if tool_file:
                    tool_path = os.path.join(self.shared_tools_dir, tool_file)
                    tool_module = self._load_tool_module(tool_path, tool_name)
                    
                    if tool_module and hasattr(tool_module, 'execute'):
                        self.shared_tools[tool_name] = {
                            'module': tool_module,
                            'info': tool_info,
                            'type': 'shared'
                        }
                        
        except Exception as e:
            print(f"Error loading shared tools: {e}")
    
    def _load_personal_tools(self):
        """Load personal tools for the specific agent."""
        if not self.agent_id:
            return
            
        agent_tools_dir = os.path.join(self.personal_tools_dir, self.agent_id)
        index_path = os.path.join(agent_tools_dir, "index.json")
        
        if not os.path.exists(index_path):
            # Create personal tools directory and index for new agent
            os.makedirs(agent_tools_dir, exist_ok=True)
            self._create_personal_index(index_path)
            return
        
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            for tool_name, tool_info in index_data.get('tools', {}).items():
                tool_file = tool_info.get('file')
                if tool_file:
                    tool_path = os.path.join(agent_tools_dir, tool_file)
                    tool_module = self._load_tool_module(tool_path, tool_name)
                    
                    if tool_module and hasattr(tool_module, 'execute'):
                        self.personal_tools[tool_name] = {
                            'module': tool_module,
                            'info': tool_info,
                            'type': 'personal'
                        }
                        
        except Exception as e:
            print(f"Error loading personal tools for {self.agent_id}: {e}")
    
    def _load_tool_module(self, tool_path: str, tool_name: str):
        """Dynamically load a tool module from file."""
        if not os.path.exists(tool_path):
            print(f"Warning: Tool file not found: {tool_path}")
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(tool_name, tool_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading tool module {tool_path}: {e}")
            return None
    
    def _create_personal_index(self, index_path: str):
        """Create an empty personal tools index."""
        index_data = {
            "tools": {},
            "metadata": {
                "agent_id": self.agent_id,
                "total_tools": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name, checking personal tools first, then shared."""
        # Check personal tools first
        if tool_name in self.personal_tools:
            return self.personal_tools[tool_name]
        
        # Then check shared tools
        if tool_name in self.shared_tools:
            return self.shared_tools[tool_name]
        
        return None
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool info metadata for the given tool name."""
        tool_data = self.get_tool(tool_name)
        if tool_data:
            return tool_data.get('info', {})
        return None
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tools with their descriptions and metadata."""
        all_tools = {}
        
        # Add shared tools
        for tool_name, tool_data in self.shared_tools.items():
            all_tools[tool_name] = {
                'name': tool_data['info']['name'],
                'description': tool_data['info']['description'],
                'energy_reward': tool_data['info']['energy_reward'],
                'parameters': tool_data['info']['parameters'],
                'type': 'shared',
                'created_by': tool_data['info'].get('created_by', 'unknown'),
                'depends_on': tool_data['info'].get('depends_on', [])
            }
        
        # Add personal tools (override shared if same name)
        for tool_name, tool_data in self.personal_tools.items():
            all_tools[tool_name] = {
                'name': tool_data['info']['name'],
                'description': tool_data['info']['description'],
                'energy_reward': tool_data['info']['energy_reward'],
                'parameters': tool_data['info']['parameters'],
                'type': 'personal',
                'created_by': tool_data['info'].get('created_by', self.agent_id),
                'depends_on': tool_data['info'].get('depends_on', [])
            }
        
        return all_tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters (no context)."""
        return self.execute_tool_with_context(tool_name, parameters, context=None)
    
    def execute_tool_with_context(self, tool_name: str, parameters: Dict[str, Any], context=None) -> Dict[str, Any]:
        """Execute a tool with given parameters and execution context."""
        tool_data = self.get_tool(tool_name)
        
        if not tool_data:
            return {
                'success': False,
                'result': f'Tool not found: {tool_name}',
                'energy_gain': 0
            }
        
        try:
            # Execute the tool with context
            if hasattr(tool_data['module'], 'execute'):
                # Try to call with context first, fall back to no context
                try:
                    result = tool_data['module'].execute(parameters, context)
                except TypeError:
                    # Fallback for tools that don't support context yet
                    result = tool_data['module'].execute(parameters)
            else:
                return {
                    'success': False,
                    'result': f'Tool "{tool_name}" has no execute method',
                    'energy_gain': 0
                }
            
            # Update usage count
            self._update_tool_usage(tool_name, tool_data['type'])
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'result': f'Tool execution error: {str(e)}',
                'energy_gain': 0
            }
    
    def _update_tool_usage(self, tool_name: str, tool_type: str):
        """Update the usage count for a tool."""
        if tool_type == 'shared':
            index_path = os.path.join(self.shared_tools_dir, "index.json")
        else:
            agent_tools_dir = os.path.join(self.personal_tools_dir, self.agent_id)
            index_path = os.path.join(agent_tools_dir, "index.json")
        
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            if tool_name in index_data.get('tools', {}):
                index_data['tools'][tool_name]['usage_count'] += 1
                index_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(index_path, 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except Exception as e:
            print(f"Error updating tool usage for {tool_name}: {e}")
    
    def create_personal_tool(self, tool_name: str, description: str, code: str, energy_reward: int = 5) -> bool:
        """Create a new personal tool for the agent."""
        if not self.agent_id:
            print("Cannot create personal tool: No agent ID provided")
            return False
        
        agent_tools_dir = os.path.join(self.personal_tools_dir, self.agent_id)
        os.makedirs(agent_tools_dir, exist_ok=True)
        
        # Create the tool file
        tool_file = f"{tool_name}.py"
        tool_path = os.path.join(agent_tools_dir, tool_file)
        
        tool_template = f'''"""
{tool_name} - {description}
Created by: {self.agent_id}
Energy Reward: {energy_reward}
"""

{code}
'''
        
        try:
            with open(tool_path, 'w') as f:
                f.write(tool_template)
            
            # Update the personal index
            index_path = os.path.join(agent_tools_dir, "index.json")
            
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    index_data = json.load(f)
            else:
                index_data = {
                    "tools": {},
                    "metadata": {
                        "agent_id": self.agent_id,
                        "total_tools": 0,
                        "last_updated": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
            
            # Add tool to index
            index_data['tools'][tool_name] = {
                "name": tool_name,
                "description": description,
                "energy_reward": energy_reward,
                "parameters": {},  # Would need to parse from code
                "file": tool_file,
                "created_by": self.agent_id,
                "usage_count": 0
            }
            
            index_data['metadata']['total_tools'] = len(index_data['tools'])
            index_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(index_path, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            # Reload personal tools
            self._load_personal_tools()
            
            print(f"✅ Created personal tool '{tool_name}' for {self.agent_id}")
            return True
            
        except Exception as e:
            print(f"Error creating personal tool '{tool_name}': {e}")
            return False
    
    def list_tools_summary(self) -> str:
        """Get a formatted summary of all available tools."""
        all_tools = self.get_available_tools()
        
        summary = f"\n🔧 AVAILABLE TOOLS ({len(all_tools)} total)\n"
        summary += "=" * 50 + "\n"
        
        # Group by type
        shared = {k: v for k, v in all_tools.items() if v['type'] == 'shared'}
        personal = {k: v for k, v in all_tools.items() if v['type'] == 'personal'}
        
        if shared:
            summary += f"\n📂 SHARED TOOLS ({len(shared)}):\n"
            for name, info in shared.items():
                deps = f" [depends: {', '.join(info['depends_on'])}]" if info['depends_on'] else ""
                summary += f"  • {name}: {info['description']} (+{info['energy_reward']} energy){deps}\n"
        
        if personal:
            summary += f"\n👤 PERSONAL TOOLS ({len(personal)}):\n"
            for name, info in personal.items():
                deps = f" [depends: {', '.join(info['depends_on'])}]" if info['depends_on'] else ""
                summary += f"  • {name}: {info['description']} (+{info['energy_reward']} energy){deps}\n"
        
        return summary 