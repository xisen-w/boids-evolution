"""
Agent Interface v1 - Phase 1.0 Implementation

Core: observe → reflect → build_tools → build_tests
Enhanced with comprehensive testing capabilities!
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Handle imports for both standalone and module usage
try:
    from .azure_client import AzureOpenAIClient
    from .tools_v1 import ToolRegistryV1
    from .environment_manager import EnvironmentManager
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from src.azure_client import AzureOpenAIClient
        from src.tools_v1 import ToolRegistryV1
        from src.environment_manager import EnvironmentManager
    except ImportError:
        print("⚠️  Azure client, tools, or environment manager not available - will use mock responses")
        AzureOpenAIClient = None
        ToolRegistryV1 = None
        EnvironmentManager = None


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
        self.environment_manager = EnvironmentManager() if EnvironmentManager else None
        self.self_built_tools = {}  # Tools I built, now a dictionary of metadata
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

        # Initialize EnvironmentManager
        self.environment_manager = EnvironmentManager(self.personal_tool_dir)
    
    def observe(self, neighbors: List['Agent'] = None) -> Dict[str, Any]:
        """
        Observe the state of the local neighborhood.
        If neighbors are provided, observation is limited to their tools.
        Otherwise, it sees all tools in the shared registry (legacy behavior).
        """
        if neighbors:
            # Boids mode: Observe only neighbors
            neighbor_tools_status = {}
            for neighbor in neighbors:
                neighbor_tools_status[neighbor.agent_id] = neighbor.self_built_tools
            
            return {
                "is_local_view": True,
                "neighbor_tools": neighbor_tools_status
            }

        # Legacy mode: Observe all shared tools
        all_visible_tools = self.shared_tool_registry.get_all_tools()
        
        # Categorize tools based on their metadata
        my_tools_status = {}
        shared_tools_status = {}
        neighbor_tools_status = {}
        
        for tool_name, tool_data in all_visible_tools.items():
            creator = tool_data.get("created_by")
            status_summary = self._summarize_test_status(tool_data)
            
            if creator == self.agent_id:
                my_tools_status[tool_name] = status_summary
            elif creator is None or "Agent" not in creator:
                shared_tools_status[tool_name] = status_summary
            else:
                if creator not in neighbor_tools_status:
                    neighbor_tools_status[creator] = {}
                neighbor_tools_status[creator][tool_name] = status_summary

        # Add detailed test results for learning from failures
        my_test_details = self._get_detailed_test_results()
        
        # Discover tools available for calling (CRITICAL for tool composition!)
        available_tools_for_calling = self._discover_available_tools_for_calling()
        
        observation = {
            "all_visible_tools": all_visible_tools,
            "my_tools": list(my_tools_status.keys()),
            "my_test_status": my_tools_status,
            "my_test_details": my_test_details,  # NEW: Detailed test results for learning
            "shared_test_status": shared_tools_status,
            "neighbor_test_status": neighbor_tools_status,
            "available_tools_for_calling": available_tools_for_calling,  # NEW: Tools this agent can call!
        }
        
        return observation
    
    def _summarize_test_status(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a consistent summary of a tool's test status."""
        test_passed = tool_data.get("test_passed")
        has_test = tool_data.get("has_test", False)
        
        summary = "No test info"
        if test_passed is True:
            summary = "✅ All tests passing"
        elif test_passed is False:
            summary = "❌ Tests failing"
        elif has_test:
            summary = "⚠️ Test exists but not run"

        return {
            "test_summary": summary,
            "test_passed": test_passed
        }
    
    def _get_detailed_test_results(self) -> Dict[str, Any]:
        """Get detailed test results for learning from failures."""
        detailed_results = {}
        
        for tool_name in self.self_built_tools.keys():
            results_file = os.path.join(self.personal_test_results_dir, f"{tool_name}_results.json")
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        test_data = json.load(f)
                    
                    # Extract key information for learning
                    detailed_results[tool_name] = {
                        "execution_success": test_data.get("execution_success", False),
                        "all_passed": test_data.get("all_passed", False),
                        "error_message": test_data.get("error", ""),
                        "failed_tests": [
                            test for test in test_data.get("tests", []) 
                            if not test.get("passed", True)
                        ],
                        "test_count": test_data.get("total_tests", 0),
                        "passed_count": test_data.get("passed_tests", 0)
                    }
                except Exception as e:
                    detailed_results[tool_name] = {
                        "execution_success": False,
                        "error_message": f"Could not read test results: {e}",
                        "all_passed": False
                    }
        
        return detailed_results

    def _discover_available_tools_for_calling(self) -> Dict[str, Any]:
        """Discover tools that this agent can call from other agents and shared tools."""
        available_tools = {}
        
        try:
            # Get all visible tools from the tool registry
            all_tools = self.shared_tool_registry.get_all_tools()
            
            for tool_name, tool_data in all_tools.items():
                # Skip tools created by this agent (we don't call our own tools)
                if tool_data.get("created_by") == self.agent_id:
                    continue
                
                # Only include tools that have passed tests (working tools)
                if tool_data.get("test_passed", False):
                    available_tools[tool_name] = {
                        "description": tool_data.get("description", "No description available"),
                        "created_by": tool_data.get("created_by", "Unknown"),
                        "file": tool_data.get("file", ""),
                        "tci_score": tool_data.get("complexity", {}).get("tci_score", 0),
                        "parameters": self._infer_tool_parameters(tool_name, tool_data)
                    }
        
        except Exception as e:
            print(f"Error discovering available tools: {e}")
        
        return available_tools

    def _infer_tool_parameters(self, tool_name: str, tool_data: Dict[str, Any]) -> Dict[str, Any]: #TODO THis is too ugly and almost useless. For parameters. opbviously the functions themselves have had them well!! 
        """Infer tool parameters from description and metadata."""
        description = tool_data.get("description", "")
        
        # Simple parameter inference based on common patterns
        params = {}
        
        if "data" in description.lower():
            params["data"] = "Any data input (list, dict, or DataFrame)"
        if "parameters" in description.lower():
            params["parameters"] = "Dictionary of tool-specific parameters"
        if "context" in description.lower():
            params["context"] = "Optional context dictionary"
        if "file" in description.lower() or "path" in description.lower():
            params["file_path"] = "Path to input file"
        if "model" in description.lower():
            params["model_params"] = "Model parameters dictionary"
        
        # Default parameters if none inferred
        if not params:
            params = {
                "data": "Input data for processing",
                "parameters": "Tool-specific parameters"
            }
        
        return params

    def reflect(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a reflection based on a dynamically constructed prompt.
        The core reflection logic is now handled by the orchestrator, making the agent a flexible actor.
        The agent no longer saves its own history; the runner is responsible for that.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        reflection = self.azure_client.chat(messages, temperature=0.7)
        return reflection

    def build_tools(self, reflection: str, round_num: int) -> Dict[str, Any]:
        """
        Build tools based on reflection.
        
        Args:
            reflection: Strategic reflection from agent
            
        Returns:
            Build result with tool info for testing

        #TODO. This is HUGE. Althought in the reflection curation part, we passed in so many 'instructions', in the code-writing for tool building, this little is here!!'
        """
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
        
        tool_design = self.azure_client.chat(messages, temperature=0.7)
        
        # Create the actual tool file
        tool_info = self._create_tool_file(tool_design, round_num)
        
        return {
            "success": tool_info["success"],
            "tool_design": tool_design,
            "tool_info": tool_info,
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
    
    def _create_tool_file(self, tool_design: str, round_num: int) -> Dict[str, Any]:
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
            
            # 🆕 NEW: Analyze tool for TCI complexity
            complexity_data = self._analyze_tool_complexity(tool_file, tool_name)
            print(f"   🔍 DEBUG: complexity_data = {complexity_data}")
            
            # Update personal tool index (with complexity data)
            tool_metadata = self._update_tool_index(tool_name, tool_design, round_num, complexity_data)
            print(f"   🔍 DEBUG: tool_metadata complexity = {tool_metadata.get('complexity', 'MISSING')}")
            
            # Add to self_built_tools
            if tool_name not in self.self_built_tools:
                self.self_built_tools[tool_name] = tool_metadata
            
            return {
                "success": True,
                "tool_name": tool_name,
                "tool_file": tool_file,
                "tool_design": tool_design
            }
            
        except Exception as e:
            print(f"Error creating tool: {e}")
            return {"success": False, "error": str(e)}
    
    
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

    def _extract_tool_name(self, tool_design: str) -> str:
        """Extract tool name from design text."""
        # Simple extraction - look for "name:" or similar patterns
        lines = tool_design.split('\n')
        for line in lines:
            if 'name:' in line.lower() or 'tool name:' in line.lower():
                # Extract the name part
                name_part = line.split(':')[1].strip()
                # Clean it up for filename - REMOVE HYPHENS for Python imports
                tool_name = ''.join(c for c in name_part if c.isalnum() or c == '_').strip()
                # Replace hyphens with underscores for Python compatibility
                tool_name = tool_name.replace('-', '_')
                if tool_name:
                    return tool_name
        
        # Fallback to generic name
        return f"tool_{len(self.self_built_tools) + 1}"
    
    def _generate_tool_code(self, tool_design: str, tool_name: str) -> str:
        """Generate Python code for the tool."""
        
        # Get available packages info
        package_examples = ""
        if self.environment_manager:
            examples = self.environment_manager.get_import_examples()
            if examples:
                package_examples = f"\n\nAVAILABLE PACKAGES (use these imports):\n" + "\n".join(examples[:8])
        
        # Use Azure to generate actual implementation
        system_prompt = f"""Generate a complete Python implementation for this tool:

{tool_design}{package_examples}

CRITICAL REQUIREMENTS:
1. Output ONLY raw Python code (no markdown, no ```)
2. Entry point must be: def execute(parameters, context=None):
3. You MAY define small helper functions to keep code readable and modular
4. Include robust error handling
5. Return a dictionary with at least THREE keys (e.g., result, details, meta)
6. Ensure all parentheses and brackets are closed
7. Try to build more complex tools (more lines). Aim for more lines total (helpers allowed) when appropriate for clarity
8. Prefer available packages listed above
9. If useful, try to call other tools for building your own tool.

🚫 ABSOLUTELY NO PLACEHOLDERS:
- NO "# TODO: implement this"
- NO "# placeholder for X"  
- NO "pass" statements as implementation
- NO "raise NotImplementedError"
- EVERY function must have complete, working implementation
- ALL logic must be fully implemented with actual code 

TOOL COMPOSITION (HIGHLY ENCOURAGED!):
- To call other tools: context.call_tool('tool_name', {{'param': value}})
- Always check: if context: before calling tools
- Example: result = context.call_tool('DataProcessor', {{'data': my_data}})
- Example: analysis = context.call_tool('Analyzer', {{'input': processed_data}})
- Build upon existing tools rather than duplicating functionality
- Create tool pipelines: Tool A → Tool B → Tool C
- This increases your TCI score and creates more valuable tools!
- Handle context=None case gracefully
- When context is available, you may leverage existing tools to build more sophisticated functionality
- If you use other tools, include a 'composition' field in the returned dict (e.g., "my_tool -> data_cleaner -> validator")

TOOL COMPOSITION - CALLING OTHER TOOLS:
If your tool needs to use other tools, use the context object:
- context.call_tool(tool_name, parameters) -> returns result dict
- Check if context exists: if context:
- Always handle the case where context is None

Example structures:
# Standalone tool:
def execute(parameters, context=None):
    \"\"\"Tool description\"\"\"
    try:
        data = parameters.get('data')
        result = process_data(data)
        return {{"result": result}}
    except Exception as e:
        return {{"error": str(e)}}

# Compositional tool:
def execute(parameters, context=None):
    \"\"\"Tool that leverages other tools\"\"\"
    try:
        data = parameters.get('data')
        
        if context:
            # Clean the data first
            clean_result = context.call_tool('DataQualityInspector', {{'df': data}})
            if clean_result.get('success'):
                # Then transform it
                transform_result = context.call_tool('DataTransformer', {{'df': data, 'config': {{}}}})
                if transform_result.get('success'):
                    return {{
                        "result": transform_result['result'], 
                        "quality_score": clean_result['overall_score'],
                        "composition": "my_tool -> DataQualityInspector -> DataTransformer"
                    }}
        
        # Fallback: process directly
        processed_data = process_data_directly(data)
        return {{"result": processed_data, "composition": "standalone"}}
    except Exception as e:
        return {{"error": str(e)}}"""

        # Get available tools for composition
        available_tools = self._discover_available_tools_for_calling()
        available_tools_info = ""
        if available_tools:
            available_tools_info = f"\n\nAVAILABLE TOOLS FOR COMPOSITION:\n"
            for tool_name, tool_info in available_tools.items():
                available_tools_info += f"- {tool_name}: {tool_info['description'][:100]}...\n"
                available_tools_info += f"  Parameters: {list(tool_info['parameters'].keys())}\n"
                available_tools_info += f"  TCI Score: {tool_info['tci_score']}\n\n"
        else:
            available_tools_info = "\n\nNo other tools available for composition yet."

        user_prompt = f"""Write a complete Python function for {tool_name}.
Consider using context.call_tool() to leverage existing tools when appropriate.
{available_tools_info}
Output ONLY the Python code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        code = self.azure_client.chat(messages, temperature=0.1, max_tokens=30000)  # Lower tokens to prevent cutoff
        
        
        # Validate package usage if environment manager is available
        if self.environment_manager:
            validation = self.environment_manager.validate_package_usage(code)
            if not validation["all_valid"] and validation["invalid_packages"]:
                print(f"⚠️  Tool {tool_name} uses unavailable packages: {validation['invalid_packages']}")
        
        return code
    
    def _extract_resource_info(self) -> str:
        """Extract resource information from meta_prompt for test generation."""
        if not self.meta_prompt:
            return ""
        
        # Look for resource references in meta_prompt
        resource_patterns = [
            "resources/task_1_crocodile_dataset.csv",
            "resources/task_2_insurance.csv", 
            "resources/task_3_GDP.csv",
            "resources/task_4_bi.csv",
            "resources/task_5_creditcard.csv",
            "resources/task_6_maths_notes.pdf",
            "resources/task_7_journey_to_the_west.pdf",
            "resources/task_8_sonnets_18.pdf",
            "resources/task_9_grid_runner_PRD.pdf",
            "resources/task_10_to_do_lite_PRD.pdf"
        ]
        
        detected_resource = None
        for pattern in resource_patterns:
            if pattern in self.meta_prompt:
                detected_resource = pattern
                break
        
        if detected_resource:
            return f"""RESOURCE CONTEXT:
This tool is designed to work with the specific resource: {detected_resource}
Your tests MUST use this actual resource file for realistic testing.
Tests should load and work with real data from this resource, not mock data.

CRITICAL RESOURCE PATH: Use this EXACT path in your tests:
resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '{detected_resource}')
This points to the correct resources directory in the project root."""
        else:
            return ""
    
    def _generate_test_code(self, tool_name: str, tool_design: str) -> str:
        """Generate comprehensive test code for a tool."""
        
        # Extract resource information from meta_prompt
        resource_info = self._extract_resource_info()
        
        system_prompt = f"""Generate comprehensive Python test code for this tool:

TOOL NAME: {tool_name}
TOOL DESIGN: {tool_design}

{resource_info}

CRITICAL REQUIREMENTS:
1. Output ONLY raw Python code (no markdown, no ```)
2. Use the EXACT template structure provided below - DO NOT MODIFY THE IMPORT SECTION
3. The import section MUST use the exact path manipulation code provided
4. Create a complete test suite with multiple test cases
5. Include positive tests, negative tests, and edge cases
6. Return detailed test results as a dictionary
7. Maximum 100 lines of code

WARNING: If you change the import section, the tests will fail completely!

CRITICAL: You MUST use this EXACT structure - do not modify the import section:

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
    
    # CRITICAL: Use this EXACT import code - DO NOT CHANGE
    try:
        import importlib.util
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Dynamic import to handle any tool name (including those with special characters)
        tool_file = os.path.join(parent_dir, f"{tool_name}.py")
        spec = importlib.util.spec_from_file_location("tool_module", tool_file)
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)
        
        # Make the tool available as {tool_name}
        globals()["{tool_name}"] = tool_module
    except Exception as e:
        results["import_error"] = str(e)
        return results
    
    def record_result(test_name, passed, error_msg=None):
        results["total_tests"] += 1
        if passed:
            results["passed_tests"] += 1
        else:
            results["failed_tests"] += 1
        results["tests"].append({{
            "test_name": test_name,
            "passed": passed,
            "error": error_msg
        }})
    
    # CRITICAL: Tools expect parameters as a dictionary!
    # CORRECT: result = {tool_name}.execute({{'param1': value1, 'param2': value2}})
    # WRONG: result = {tool_name}.execute(value1, value2)
    
    # Example test case - EXTREMELY LENIENT:
    try:
        # Call tool with basic parameters
        result = {tool_name}.execute({{'data': [1, 2, 3]}})
        # Accept ANY result that doesn't crash
        if result is not None:
            record_result("Basic functionality", True)
        else:
            record_result("Basic functionality", False, "Tool returned None")
    except Exception as e:
        record_result("Basic functionality", False, str(e))
    
    # Add more test cases following the same pattern...
    results["all_passed"] = results["failed_tests"] == 0
    return results

if __name__ == "__main__":
    test_results = run_tests()
    print(json.dumps(test_results, indent=2))"""

        user_prompt = f"""Create comprehensive, resource-aware tests for {tool_name}.

CRITICAL IMPORT REQUIREMENT: Use the EXACT import template provided above. DO NOT change the import section or the tests will fail completely.

CRITICAL: Tools use this calling convention:
- result = {tool_name}.execute({{'param1': value1, 'param2': value2}})
- NOT: result = {tool_name}.execute(value1, value2)

RESOURCE-FOCUSED TESTING REQUIREMENTS:
1. If a resource file is specified, your tests MUST attempt to load and use real data from that resource
2. Design tests to be modular and minimal but use actual resource data when available
3. Test realistic scenarios that the tool would encounter with the actual resource
4. Include error handling tests for resource access issues
5. Validate that the tool produces meaningful results with real data

GENERATE 3 COMPREHENSIVE TEST CASES:
1. **Resource Integration Test**: Load actual data from the specified resource and test core functionality
2. **Error Handling Test**: Test behavior when resource is unavailable or malformed
3. **Edge Case Test**: Test with boundary conditions from the actual resource data

TESTING PHILOSOPHY:
- Use real data when possible, not just mock data
- Test meaningful functionality, not just basic execution
- Validate that results make sense for the specific domain/resource
- Ensure tests help identify actual issues with tool implementation

REMINDER: Use the EXACT template structure above - especially the import section.
Output ONLY the Python test code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            test_code = self.azure_client.chat(messages, temperature=0.1, max_tokens=30000)
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
            "test_execution_success": None,
            "complexity": {}  # Default empty complexity data
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
    
    def _update_tool_index(self, tool_name: str, tool_design: str, round_num: int, complexity_data: Dict = None) -> Dict[str, Any]:
        """Update the personal tool index JSON and return the new tool's metadata."""
        index_file = f"{self.personal_tool_dir}/index.json"
        index_data = self._load_index_json(index_file)
        
        # Add new tool with test status fields
        tool_entry = {
            "name": tool_name,
            "description": tool_design[:200] + "..." if len(tool_design) > 200 else tool_design,
            "file": f"{tool_name}.py",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat(),
            "created_in_round": round_num,
            "adoption_count": 0
        }
        # DRY: Add test status fields
        tool_entry.update(self._get_default_test_status_fields(tool_name))
        # Preserve provided complexity data (do this AFTER adding defaults so we don't overwrite)
        if complexity_data is not None:
            tool_entry["complexity"] = complexity_data
        
        index_data["tools"][tool_name] = tool_entry
        self._save_index_json(index_file, index_data)
        return tool_entry
    
    def update_tool_complexity(self, tool_name: str, tci_data: Dict[str, Any]):
        """Update the tool index with its TCI complexity score."""
        index_file = os.path.join(self.personal_tool_dir, "index.json")
        index_data = self._load_index_json(index_file)
        
        if tool_name in index_data.get("tools", {}):
            # Ensure complexity key exists
            if "complexity" not in index_data["tools"][tool_name]:
                index_data["tools"][tool_name]["complexity"] = {}
            
            # Update with TCI data
            index_data["tools"][tool_name]["complexity"].update({
                "tci_score": tci_data.get("tci_score"),
                "tci_raw": tci_data.get("tci_raw"),
                "code_complexity": tci_data.get("code_complexity"),
                "interface_complexity": tci_data.get("interface_complexity"),
                "compositional_complexity": tci_data.get("compositional_complexity"),
                # Detailed metrics for analysis
                "lines_of_code": tci_data.get("lines_of_code"),
                "param_count": tci_data.get("param_count"),
                "tool_calls": tci_data.get("tool_calls"),
                "external_imports": tci_data.get("external_imports")
            })
            
            if self._save_index_json(index_file, index_data):
                print(f"   🔬 Updated complexity for {tool_name} in index.json")
    
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
    print(f"   Neighbor tools: {observation['neighbor_test_status']}")
    print(f"   My tools: {observation['my_tools']}")
    print(f"   My tests: {observation['my_test_status']}")
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
        build_result = agent.build_tools(reflection, 1) # Pass round_num
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
        
        latest_tool = list(agent.self_built_tools.keys())[-1] # Get the name of the latest tool
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