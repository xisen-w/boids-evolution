"""
Agent Interface v1 - Phase 1.0 Implementation

Core: observe → reflect → build_tools
Exactly as specified - no extra complexity!
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Handle imports for both standalone and module usage
try:
    from .azure_client import AzureOpenAIClient
    from .tools_v1 import ToolRegistryV1
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from src.azure_client import AzureOpenAIClient
        from src.tools_v1 import ToolRegistryV1
    except ImportError:
        print("⚠️  Azure client or tools not available - will use mock responses")
        AzureOpenAIClient = None
        ToolRegistryV1 = None


class Agent:
    """
    Phase 1.0 Agent - Exactly as specified
    
    Core loop: observe → reflect → build_tools
    """
    
    def __init__(self, 
                 agent_id: str,
                 azure_client: AzureOpenAIClient,
                 shared_tool_registry,  # All visible tools
                 meta_prompt: str = "",  # Shared across agents
                 envs_available: List[str] = None,
                 specific_prompt: Optional[str] = None,
                 personal_tool_base_dir: str = "personal_tools"):  # Allow custom base directory
        
        self.agent_id = agent_id
        self.azure_client = azure_client
        self.shared_tool_registry = shared_tool_registry  # All tools it can see
        self.self_built_tools = []  # Tools I built
        self.reflection_history = []  # Tools seen each time + reflections
        self.meta_prompt = meta_prompt  # Shared across agents
        self.envs_available = envs_available or ["python", "file_system"]
        self.specific_prompt = specific_prompt  # Leave as blank and render complete prompt
        
        # Create personal tool directory (can be experiment-specific)
        self.personal_tool_dir = os.path.join(personal_tool_base_dir, self.agent_id)
        os.makedirs(self.personal_tool_dir, exist_ok=True)
    
    def observe(self) -> Dict[str, Any]:
        """
        Observe current state - get neighbor tools and all visible tools.
        
        Returns:
            Observation dict with tools seen
        """
        # Get all tools from registry
        all_visible_tools = self.shared_tool_registry.get_all_tools()
        
        # Get neighbor tools (from personal_tools directories)
        neighbor_tools = self._get_neighbor_tools()
        
        observation = {
            "all_visible_tools": all_visible_tools,
            "neighbor_tools": neighbor_tools,
            "my_tools": self.self_built_tools
        }
        
        return observation
    
    def _get_neighbor_tools(self) -> Dict[str, List[str]]:
        """Get tools built by other agents (neighbors)."""
        neighbor_tools = {}
        
        if not os.path.exists("personal_tools"):
            return neighbor_tools
        
        # Look at all agent directories
        for agent_dir in os.listdir("personal_tools"):
            if agent_dir == self.agent_id:
                continue  # Skip myself
                
            agent_path = os.path.join("personal_tools", agent_dir)
            if not os.path.isdir(agent_path):
                continue
                
            index_file = os.path.join(agent_path, "index.json")
            if os.path.exists(index_file):
                try:
                    with open(index_file, 'r') as f:
                        agent_index = json.load(f)
                    neighbor_tools[agent_dir] = list(agent_index.get("tools", {}).keys())
                except:
                    neighbor_tools[agent_dir] = []
            else:
                neighbor_tools[agent_dir] = []
        
        return neighbor_tools
    
    def reflect(self, observation: Dict[str, Any]) -> str:
        """
        Prompt here to trigger reflection for the agents.
        
        Args:
            observation: Current tools seen
            
        Returns:
            Reflection text from agent
        """
        # Build complete reflection prompt
        system_prompt = f"""You are Agent {self.agent_id} in a tool-building ecosystem.

META CONTEXT: {self.meta_prompt}

AVAILABLE ENVIRONMENTS: {', '.join(self.envs_available)}

Reflect on the current tool ecosystem and think strategically about what to build next."""

        if self.specific_prompt:
            system_prompt += f"\n\nSPECIFIC GUIDANCE: {self.specific_prompt}"
        
        user_prompt = f"""CURRENT OBSERVATION:

All Visible Tools: {len(observation['all_visible_tools'])} tools
{list(observation['all_visible_tools'].keys())[:10]}  # Show first 10

Neighbor Tools:
{observation['neighbor_tools']}

My Tools Built: {len(observation['my_tools'])} tools
{observation['my_tools']}

Reflect on:
1. What gaps do you see in the current tool ecosystem?
2. What would be most valuable to build next?
3. What specific tool should you create?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        reflection = self.azure_client.chat(messages, temperature=0.7)
        
        # Store in reflection history
        reflection_entry = {
            "tools_seen": list(observation['all_visible_tools'].keys()),
            "neighbor_tools": observation['neighbor_tools'],
            "reflection": reflection,
            "timestamp": datetime.now().isoformat()
        }
        
        self.reflection_history.append(reflection_entry)
        
        return reflection
    
    def build_tools(self, reflection: str) -> Dict[str, Any]:
        """
        Build tools based on reflection.
        
        Args:
            reflection: Strategic reflection from agent
            
        Returns:
            Build result
        """
        # Use Azure to decide what specific tool to build
        system_prompt = f"""You are Agent {self.agent_id}. Based on your reflection, design a specific tool to build.

Create a tool specification with:
- Unique tool name
- Clear description
- Tool type (data, logic, utility, code)
- Implementation outline"""

        user_prompt = f"""REFLECTION: {reflection}

Based on this reflection, design ONE specific tool to build.
Be concrete and practical."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        tool_design = self.azure_client.chat(messages, temperature=0.5)
        
        # Create the actual tool file
        success = self._create_tool_file(tool_design)
        
        return {
            "success": success,
            "tool_design": tool_design,
            "reflection": reflection
        }
    
    def _create_tool_file(self, tool_design: str) -> bool:
        """Create actual Python file for the tool."""
        try:
            # Extract tool name from design
            tool_name = self._extract_tool_name(tool_design)
            
            # Generate Python code
            python_code = self._generate_tool_code(tool_design, tool_name)
            
            # Write tool file
            tool_file = f"{self.personal_tool_dir}/{tool_name}.py"
            with open(tool_file, 'w') as f:
                f.write(python_code)
            
            # Update personal tool index
            self._update_tool_index(tool_name, tool_design)
            
            # Add to self_built_tools
            self.self_built_tools.append(tool_name)
            
            return True
            
        except Exception as e:
            print(f"Error creating tool: {e}")
            return False
    
    def _extract_tool_name(self, tool_design: str) -> str:
        """Extract tool name from design text."""
        # Simple extraction - look for "name:" or similar patterns
        lines = tool_design.split('\n')
        for line in lines:
            if 'name:' in line.lower() or 'tool name:' in line.lower():
                # Extract the name part
                name_part = line.split(':')[1].strip()
                # Clean it up for filename
                tool_name = ''.join(c for c in name_part if c.isalnum() or c in '_-').strip()
                if tool_name:
                    return tool_name
        
        # Fallback to generic name
        return f"tool_{len(self.self_built_tools) + 1}"
    
    def _generate_tool_code(self, tool_design: str, tool_name: str) -> str:
        """Generate Python code for the tool."""
        
        # Use Azure to generate actual implementation
        system_prompt = f"""Generate a simple, complete Python function for this tool:

{tool_design}

REQUIREMENTS:
1. Output ONLY raw Python code (no markdown, no ```)
2. Create ONE complete function: def execute(parameters, context=None):
3. Keep it simple but functional
4. Include basic error handling
5. Return a dictionary with results
6. Ensure all parentheses and brackets are closed
7. Maximum 50 lines of code

Example structure:
def execute(parameters, context=None):
    \"\"\"Tool description\"\"\"
    try:
        # Get parameters
        data = parameters.get('data')
        # Do the work
        result = process_data(data)
        return {{"result": result}}
    except Exception as e:
        return {{"error": str(e)}}"""

        user_prompt = f"""Write a simple, complete Python function for {tool_name}.
Keep it under 50 lines.
Output ONLY the Python code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        code = self.azure_client.chat(messages, temperature=0.1, max_tokens=500)  # Lower tokens to prevent cutoff
        
        return code
    
    def _update_tool_index(self, tool_name: str, tool_design: str):
        """Update the personal tool index JSON."""
        index_file = f"{self.personal_tool_dir}/index.json"
        
        # Load existing index
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
        else:
            index_data = {"tools": {}}
        
        # Add new tool
        index_data["tools"][tool_name] = {
            "name": tool_name,
            "description": tool_design[:200] + "..." if len(tool_design) > 200 else tool_design,
            "file": f"{tool_name}.py",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)


def main():
    """Test the Agent tool creation and reflection process."""
    
    print("🧪 Testing Agent v1 - Tool Creation and Reflection")
    print("=" * 60)
    
    # Initialize Azure OpenAI client
    if AzureOpenAIClient:
        try:
            azure_client = AzureOpenAIClient()
            print("✅ Azure OpenAI client initialized")
        except Exception as e:
            print(f"❌ Azure client failed: {e}")
            return
    else:
        print("❌ Azure client not available")
        return
    
    # Create sample tool registry
    tool_registry = ToolRegistryV1()
    print(f"✅ Tool registry created with {len(tool_registry.get_all_tools())} sample tools")
    
    # Create test agent
    meta_prompt = "You are in a collaborative tool-building environment. Your specialty is SORTING and ORDERING algorithms. Focus on creating practical sorting tools that can handle different data types and use cases."
    
    agent = Agent(
        agent_id="TestAgent_01",
        azure_client=azure_client,
        shared_tool_registry=tool_registry,
        meta_prompt=meta_prompt,
        envs_available=["python", "file_system", "data_processing"],
        specific_prompt="Focus on building advanced sorting tools - quick sort, merge sort, custom comparators, multi-key sorting."
    )
    
    print(f"✅ Agent {agent.agent_id} created")
    
    # Test 1: Observe
    print(f"\n🔍 Test 1: Observe Current State")
    print("-" * 40)
    
    observation = agent.observe()
    print(f"   Visible tools: {len(observation['all_visible_tools'])}")
    print(f"   Tool names: {list(observation['all_visible_tools'].keys())}")
    print(f"   Neighbor tools: {observation['neighbor_tools']}")
    print(f"   My tools: {observation['my_tools']}")
    
    # Test 2: Reflect
    print(f"\n💭 Test 2: Agent Reflection")
    print("-" * 40)
    
    try:
        reflection = agent.reflect(observation)
        print(f"   Reflection generated:")
        print(f"   {reflection[:200]}...")
    except Exception as e:
        print(f"   Reflection failed: {e}")
        return
    
    # Test 3: Build Tools
    print(f"\n🔨 Test 3: Build Tools")
    print("-" * 40)
    
    try:
        build_result = agent.build_tools(reflection)
        print(f"   Build success: {build_result['success']}")
        if build_result['success']:
            print(f"   Tool design: {build_result['tool_design'][:150]}...")
            print(f"   Tools built: {agent.self_built_tools}")
    except Exception as e:
        print(f"   Build failed: {e}")
        return
    
    # Test 4: Verify state
    print(f"\n📊 Test 4: Final Agent State")
    print("-" * 40)
    
    final_observation = agent.observe()
    print(f"   Tools built: {len(agent.self_built_tools)}")
    print(f"   Self-built tools: {agent.self_built_tools}")
    print(f"   Reflection history: {len(agent.reflection_history)} entries")
    print(f"   Personal tool directory: {agent.personal_tool_dir}")
    
    # Check if tool files were created
    if os.path.exists(agent.personal_tool_dir):
        files = os.listdir(agent.personal_tool_dir)
        print(f"   Files created: {files}")
        
        # Show tool index
        index_file = f"{agent.personal_tool_dir}/index.json"
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            print(f"   Tool index: {list(index_data.get('tools', {}).keys())}")
    
    # Test 5: Show created tool content
    if agent.self_built_tools:
        print(f"\n🔧 Test 5: Inspect Created Tool")
        print("-" * 40)
        
        latest_tool = agent.self_built_tools[-1]
        tool_file = f"{agent.personal_tool_dir}/{latest_tool}.py"
        
        if os.path.exists(tool_file):
            with open(tool_file, 'r') as f:
                tool_code = f.read()
            print(f"   Tool file: {latest_tool}.py")
            print(f"   Code preview:")
            print("   " + "\n   ".join(tool_code[:300].split('\n')))
            if len(tool_code) > 300:
                print("   ...")
    
    print(f"\n✅ Agent v1 testing completed!")
    print(f"   Core loop tested: observe → reflect → build_tools")
    print(f"   Agent successfully created tools and maintained reflection history")


if __name__ == "__main__":
    main() 