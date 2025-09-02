"""
Agent Interface v1 - Phase 1.0 Implementation

Core: observe → reflect → build_tools → build_tests
Enhanced with comprehensive testing capabilities!
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
    Phase 1.0 Agent - Enhanced with Testing Capabilities
    
    Core loop: observe → reflect → build_tools → build_tests
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
        self.self_built_tests = []  # Tests I built
        self.reflection_history = []  # Tools seen each time + reflections
        self.test_results_history = []  # Test execution results
        self.meta_prompt = meta_prompt  # Shared across agents
        self.envs_available = envs_available or ["python", "file_system"]
        self.specific_prompt = specific_prompt  # Leave as blank and render complete prompt
        
        # Create personal tool directory structure (can be experiment-specific)
        self.personal_tool_dir = os.path.join(personal_tool_base_dir, self.agent_id)
        self.personal_tests_dir = os.path.join(self.personal_tool_dir, "_tests")
        self.personal_test_results_dir = os.path.join(self.personal_tool_dir, "_testResults")
        
        # Create all necessary directories
        os.makedirs(self.personal_tool_dir, exist_ok=True)
        os.makedirs(self.personal_tests_dir, exist_ok=True)
        os.makedirs(self.personal_test_results_dir, exist_ok=True)
    
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
        
        # Get test status for tools
        test_status = self._get_test_status()
        
        observation = {
            "all_visible_tools": all_visible_tools,
            "neighbor_tools": neighbor_tools,
            "my_tools": self.self_built_tools,
            "my_tests": self.self_built_tests,
            "test_status": test_status
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
    
    def _get_test_status(self) -> Dict[str, Dict[str, Any]]:
        """Get test status for all my tools."""
        test_status = {}
        
        for tool_name in self.self_built_tools:
            test_file = os.path.join(self.personal_tests_dir, f"{tool_name}_test.py")
            results_file = os.path.join(self.personal_test_results_dir, f"{tool_name}_results.json")
            
            status = {
                "has_test": os.path.exists(test_file),
                "has_results": os.path.exists(results_file),
                "last_tested": None,
                "test_passed": None
            }
            
            # Get latest test results
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        results = json.load(f)
                    status["last_tested"] = results.get("timestamp")
                    status["test_passed"] = results.get("all_passed", False)
                except:
                    pass
                    
            test_status[tool_name] = status
        
        return test_status
    
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

My Tests Built: {len(observation['my_tests'])} tests
{observation['my_tests']}

Test Status:
{observation['test_status']}

Reflect on:
1. What gaps do you see in the current tool ecosystem?
2. What would be most valuable to build next?
3. Do any of your tools need testing?
4. What specific tool should you create?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        reflection = self.azure_client.chat(messages, temperature=0.7)
        
        # Store in reflection history
        reflection_entry = {
            "tools_seen": list(observation['all_visible_tools'].keys()),
            "neighbor_tools": observation['neighbor_tools'],
            "test_status": observation['test_status'],
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
            Build result with tool info for testing
        """
        # Use Azure to decide what specific tool to build
        system_prompt = f"""You are Agent {self.agent_id}. Based on your reflection, design a specific tool to build.

Create a tool specification with:
- Unique tool name
- Clear description
- Tool type (data, logic, utility, code)
- Implementation outline
- Expected parameters and return format"""

        user_prompt = f"""REFLECTION: {reflection}

Based on this reflection, design ONE specific tool to build.
Be concrete and practical."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        tool_design = self.azure_client.chat(messages, temperature=0.5)
        
        # Create the actual tool file
        tool_info = self._create_tool_file(tool_design)
        
        return {
            "success": tool_info["success"],
            "tool_design": tool_design,
            "tool_info": tool_info,  # Pass tool info for testing
            "reflection": reflection
        }
    
    def build_tests(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive tests for a specific tool.
        
        Args:
            tool_info: Information about the tool to test
            
        Returns:
            Test build and execution results
        """
        if not tool_info.get("success"):
            return {"success": False, "error": "Cannot test failed tool creation"}
        
        tool_name = tool_info.get("tool_name")
        tool_design = tool_info.get("tool_design", "")
        
        if not tool_name:
            return {"success": False, "error": "No tool name provided"}
        
        # Generate test cases and test runner
        test_code = self._generate_test_code(tool_name, tool_design)
        
        if not test_code:
            return {"success": False, "error": "Failed to generate test code"}
        
        # Create test file
        test_success = self._create_test_file(tool_name, test_code)
        
        if not test_success:
            return {"success": False, "error": "Failed to create test file"}
        
        # Execute tests immediately
        test_results = self._execute_tests(tool_name)
        
        # Add to self_built_tests
        if f"{tool_name}_test" not in self.self_built_tests:
            self.self_built_tests.append(f"{tool_name}_test")
        
        return {
            "success": True,
            "tool_name": tool_name,
            "test_file_created": test_success,
            "test_results": test_results
        }
    
    def test_tool(self, tool_name: str, force_regenerate: bool = False) -> Dict[str, Any]:
        """
        Test any available tool (DRY - reusable for any tool).
        
        Args:
            tool_name: Name of tool to test
            force_regenerate: Whether to regenerate test even if it exists
            
        Returns:
            Test execution results
        """
        # Check if tool exists
        all_tools = self.shared_tool_registry.get_all_tools()
        
        if tool_name not in all_tools:
            return {"success": False, "error": f"Tool {tool_name} not found"}
        
        tool_metadata = all_tools[tool_name]
        
        # Check if test already exists
        test_file = os.path.join(self.personal_tests_dir, f"{tool_name}_test.py")
        
        if not os.path.exists(test_file) or force_regenerate:
            # Generate test for this tool
            tool_description = tool_metadata.get("description", "No description available")
            test_code = self._generate_test_code(tool_name, tool_description)
            
            if test_code:
                self._create_test_file(tool_name, test_code)
            else:
                return {"success": False, "error": "Failed to generate test code"}
        
        # Execute tests
        test_results = self._execute_tests(tool_name)
        
        return {
            "success": True,
            "tool_name": tool_name,
            "test_results": test_results
        }
    
    def _create_tool_file(self, tool_design: str) -> Dict[str, Any]:
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
            if tool_name not in self.self_built_tools:
                self.self_built_tools.append(tool_name)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "tool_file": tool_file,
                "tool_design": tool_design
            }
            
        except Exception as e:
            print(f"Error creating tool: {e}")
            return {"success": False, "error": str(e)}
    
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
    
    def _generate_test_code(self, tool_name: str, tool_design: str) -> str:
        """Generate comprehensive test code for a tool."""
        
        system_prompt = f"""Generate comprehensive Python test code for this tool:

TOOL NAME: {tool_name}
TOOL DESIGN: {tool_design}

REQUIREMENTS:
1. Output ONLY raw Python code (no markdown, no ```)
2. Create a complete test suite with multiple test cases
3. Import the tool module and test its execute() function
4. Include positive tests, negative tests, and edge cases
5. Use try/except for error handling
6. Return detailed test results as a dictionary
7. Maximum 100 lines of code

Example structure:
import sys
import os
import json
from datetime import datetime

def run_tests():
    \"\"\"Run all tests for {tool_name}\"\"\"
    results = {{
        "tool_name": "{tool_name}",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "all_passed": False
    }}
    
    # Import the tool
    try:
        sys.path.append(os.path.dirname(__file__))
        import {tool_name}
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    # Test cases here...
    
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))"""

        user_prompt = f"""Create comprehensive tests for {tool_name}.
Generate at least 3-5 different test cases covering:
- Normal usage
- Edge cases  
- Error conditions
- Parameter validation

Output ONLY the Python test code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            test_code = self.azure_client.chat(messages, temperature=0.1, max_tokens=800)
            return test_code
        except Exception as e:
            print(f"Error generating test code: {e}")
            return ""
    
    def _create_test_file(self, tool_name: str, test_code: str) -> bool:
        """Create test file in _tests directory."""
        try:
            test_file = os.path.join(self.personal_tests_dir, f"{tool_name}_test.py")
            
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            print(f"✅ Created test file: {test_file}")
            return True
            
        except Exception as e:
            print(f"Error creating test file: {e}")
            return False
    
    def _execute_tests(self, tool_name: str) -> Dict[str, Any]:
        """Execute tests for a tool and save results."""
        test_file = os.path.join(self.personal_tests_dir, f"{tool_name}_test.py")
        results_file = os.path.join(self.personal_test_results_dir, f"{tool_name}_results.json")
        
        if not os.path.exists(test_file):
            return {"error": f"Test file not found: {test_file}"}
        
        try:
            # Execute test file and capture results
            import subprocess
            import sys
            
            # FIX: Use relative path to avoid path duplication
            relative_test_file = os.path.join("_tests", f"{tool_name}_test.py")
            
            result = subprocess.run(
                [sys.executable, relative_test_file],
                cwd=self.personal_tool_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse JSON output from test
                try:
                    test_results = json.loads(result.stdout)
                except:
                    test_results = {
                        "tool_name": tool_name,
                        "timestamp": datetime.now().isoformat(),
                        "raw_output": result.stdout,
                        "execution_success": True,
                        "parse_error": "Could not parse test results as JSON"
                    }
            else:
                test_results = {
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat(),
                    "execution_success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
            
            # Save test results
            with open(results_file, 'w') as f:
                json.dump(test_results, f, indent=2)
            
            # Add to test results history
            self.test_results_history.append(test_results)
            
            # FIX: Update tool index with test status
            self._update_tool_test_status(tool_name, test_results)
            
            return test_results
            
        except Exception as e:
            error_results = {
                "tool_name": tool_name,
                "timestamp": datetime.now().isoformat(),
                "execution_success": False,
                "error": str(e)
            }
            
            # Save error results
            with open(results_file, 'w') as f:
                json.dump(error_results, f, indent=2)
            
            # FIX: Update tool index with failed test status
            self._update_tool_test_status(tool_name, error_results)
                
            return error_results
    
    def _get_default_test_status_fields(self, tool_name: str) -> Dict[str, Any]:
        """DRY: Get default test status fields for any tool."""
        return {
            "has_test": False,
            "test_file": f"_tests/{tool_name}_test.py",
            "test_results_file": f"_testResults/{tool_name}_results.json",
            "test_passed": None,
            "last_tested": None,
            "test_execution_success": None
        }
    
    def _load_index_json(self, index_file: str) -> Dict[str, Any]:
        """DRY: Load index JSON with error handling."""
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading {index_file}: {e}")
                return {"tools": {}}
        return {"tools": {}}
    
    def _save_index_json(self, index_file: str, index_data: Dict[str, Any]) -> bool:
        """DRY: Save index JSON with error handling."""
        try:
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  Error saving {index_file}: {e}")
            return False
    
    def _update_tool_index(self, tool_name: str, tool_design: str):
        """Update the personal tool index JSON."""
        index_file = f"{self.personal_tool_dir}/index.json"
        index_data = self._load_index_json(index_file)
        
        # Add new tool with test status fields
        tool_entry = {
            "name": tool_name,
            "description": tool_design[:200] + "..." if len(tool_design) > 200 else tool_design,
            "file": f"{tool_name}.py",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat()
        }
        # DRY: Add test status fields
        tool_entry.update(self._get_default_test_status_fields(tool_name))
        
        index_data["tools"][tool_name] = tool_entry
        self._save_index_json(index_file, index_data)
    
    def _update_tool_test_status(self, tool_name: str, test_results: Dict[str, Any]):
        """Update tool index with test execution results."""
        index_file = f"{self.personal_tool_dir}/index.json"
        index_data = self._load_index_json(index_file)
        
        # Update test status for the tool
        if tool_name in index_data.get("tools", {}):
            tool_entry = index_data["tools"][tool_name]
            tool_entry["has_test"] = True
            tool_entry["last_tested"] = test_results.get("timestamp")
            tool_entry["test_execution_success"] = test_results.get("execution_success", False)
            tool_entry["test_passed"] = test_results.get("all_passed", False)
            
            if self._save_index_json(index_file, index_data):
                print(f"✅ Updated test status for {tool_name} in index.json")
    
    def save_reflection_history(self):
        """Save agent's reflection history to experiment directory."""
        reflection_file = os.path.join(self.personal_tool_dir, "reflection_history.json")
        
        reflection_data = {
            "agent_id": self.agent_id,
            "total_reflections": len(self.reflection_history),
            "meta_prompt": self.meta_prompt,
            "specific_prompt": self.specific_prompt,
            "created_at": datetime.now().isoformat(),
            "reflections": self.reflection_history
        }
        
        try:
            with open(reflection_file, 'w') as f:
                json.dump(reflection_data, f, indent=2)
            print(f"💭 Saved {len(self.reflection_history)} reflections for {self.agent_id}")
            return True
        except Exception as e:
            print(f"⚠️  Error saving reflection history: {e}")
            return False


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
    print(f"   My tests: {observation['my_tests']}")
    print(f"   Test status: {observation['test_status']}")
    
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
    
    # Test 4: Build Tests
    print(f"\n🧪 Test 4: Build Tests")
    print("-" * 40)
    
    try:
        test_result = agent.build_tests(build_result['tool_info'])
        print(f"   Test build success: {test_result['success']}")
        if test_result['success']:
            print(f"   Test file created: {test_result['test_file_created']}")
            print(f"   Test results: {test_result['test_results']}")
    except Exception as e:
        print(f"   Test build failed: {e}")
        return
    
    # Test 5: Test a specific tool
    print(f"\n🧪 Test 5: Test a Specific Tool")
    print("-" * 40)
    
    try:
        test_result = agent.test_tool("tool_1") # Assuming tool_1 was built in previous steps
        print(f"   Tool test success: {test_result['success']}")
        if test_result['success']:
            print(f"   Test results: {test_result['test_results']}")
    except Exception as e:
        print(f"   Tool test failed: {e}")
        return
    
    # Test 6: Verify state
    print(f"\n📊 Test 6: Final Agent State")
    print("-" * 40)
    
    final_observation = agent.observe()
    print(f"   Tools built: {len(agent.self_built_tools)}")
    print(f"   Self-built tools: {agent.self_built_tools}")
    print(f"   Tests built: {len(agent.self_built_tests)}")
    print(f"   Self-built tests: {agent.self_built_tests}")
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
    
    # Test 7: Show created tool content
    if agent.self_built_tools:
        print(f"\n🔧 Test 7: Inspect Created Tool")
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
    
    # Test 8: Show test results
    if agent.test_results_history:
        print(f"\n📊 Test 8: Test Results History")
        print("-" * 40)
        for test_result in agent.test_results_history:
            print(f"   Tool: {test_result.get('tool_name', 'N/A')}")
            print(f"   Timestamp: {test_result.get('timestamp', 'N/A')}")
            print(f"   Execution Success: {test_result.get('execution_success', 'N/A')}")
            print(f"   Error: {test_result.get('error', 'N/A')}")
            print(f"   Test Passed: {test_result.get('test_passed', 'N/A')}")
            print(f"   Last Tested: {test_result.get('last_tested', 'N/A')}")
            print("-" * 20)
    
    print(f"\n✅ Agent v1 testing completed!")
    print(f"   Core loop tested: observe → reflect → build_tools → build_tests")
    print(f"   Agent successfully created tools, tests, and maintained reflection history")


if __name__ == "__main__":
    main() 