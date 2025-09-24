"""
Proper Tool Boids Agent - Creates REAL computational tools with actual logic

FIXED ISSUES:
- No more trivial "improved_X" wrapper functions
- Real computational diversity (math, string, logic, data processing)
- Meaningful tool creation that adds actual value
- Proper complexity progression
"""

import os
import json
import random
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from .enhanced_tools import EnhancedToolRegistry


class ProperToolBoid:
    """
    Boids agent that creates REAL computational tools with actual logic.
    
    Each tool is a unique computational function, not a wrapper.
    """
    
    def __init__(self, agent_id: str, azure_client=None):
        self.agent_id = agent_id
        self.azure_client = azure_client
        
        # Real tool registry
        self.tool_registry = EnhancedToolRegistry(agent_id)
        
        # Boids state
        self.neighbors = []
        self.recent_actions = []
        
        # Boids rule weights
        self.separation_weight = 0.4
        self.alignment_weight = 0.3  
        self.cohesion_weight = 0.3
        
        # REAL tool generation patterns
        self.tool_generators = {
            'math': self._generate_math_tool,
            'string': self._generate_string_tool,
            'logic': self._generate_logic_tool,
            'data': self._generate_data_tool,
            'crypto': self._generate_crypto_tool,
            'analysis': self._generate_analysis_tool
        }
        
        # Track what's been created to avoid duplicates
        self.created_functions = set()
        
    def set_neighbors(self, neighbors: List['ProperToolBoid']):
        """Set network neighbors for boids observations."""
        self.neighbors = neighbors
        
    def observe_neighbors(self) -> Dict[str, Any]:
        """Observe what neighbors have created and done."""
        neighbor_tools = []
        neighbor_actions = []
        
        for neighbor in self.neighbors:
            # Get neighbor's personal tool names
            neighbor_personal_tools = [name for name, info in neighbor.tool_registry.get_available_tools().items() 
                                     if info['created_by'] == neighbor.agent_id]
            neighbor_tools.append(neighbor_personal_tools)
            
            # Get neighbor's recent actions
            neighbor_actions.append(neighbor.recent_actions[-3:] if neighbor.recent_actions else [])
            
        return {
            'neighbor_tools': neighbor_tools,
            'neighbor_actions': neighbor_actions
        }
    
    def apply_separation_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """SEPARATION: Avoid creating similar tools to neighbors."""
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0, 
            'rest': 1.0
        }
        
        # Count neighbor tool types
        neighbor_tool_types = []
        for neighbor_tools in observations['neighbor_tools']:
            for tool_name in neighbor_tools[-2:]:  # Recent tools
                tool_type = tool_name.split('_')[0] if '_' in tool_name else 'unknown'
                neighbor_tool_types.append(tool_type)
        
        # If neighbors created many tools recently, prefer using instead
        if len(neighbor_tool_types) >= 2:
            preferences['create_tool'] *= 0.5
            preferences['use_tool'] *= 1.5
            
        return preferences
    
    def apply_alignment_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """ALIGNMENT: Copy strategies of successful neighbors."""
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0,
            'rest': 1.0
        }
        
        # Find most successful neighbor (most tools)
        my_tool_count = len([name for name, info in self.tool_registry.get_available_tools().items() 
                           if info['created_by'] == self.agent_id])
        
        successful_neighbor_actions = []
        for i, neighbor_tools in enumerate(observations['neighbor_tools']):
            if len(neighbor_tools) > my_tool_count:
                neighbor_actions = observations['neighbor_actions'][i]
                successful_neighbor_actions.extend(neighbor_actions)
        
        # Boost preferences for successful actions
        for action in successful_neighbor_actions:
            if action in preferences:
                preferences[action] *= 1.3
                
        return preferences
    
    def apply_cohesion_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """COHESION: Use neighbors' tools when available."""
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0,
            'rest': 1.0
        }
        
        # Count available neighbor tools
        total_neighbor_tools = sum(len(tools) for tools in observations['neighbor_tools'])
        
        if total_neighbor_tools > 0:
            preferences['use_tool'] *= 2.0
        else:
            preferences['create_tool'] *= 1.5
            
        return preferences
    
    def choose_action(self, sep_prefs: Dict[str, float], align_prefs: Dict[str, float], cohes_prefs: Dict[str, float]) -> str:
        """Combine boids rule preferences to choose an action."""
        actions = ['create_tool', 'use_tool', 'rest']
        
        # Weighted combination
        final_prefs = {}
        for action in actions:
            final_prefs[action] = (
                sep_prefs[action] * self.separation_weight +
                align_prefs[action] * self.alignment_weight + 
                cohes_prefs[action] * self.cohesion_weight
            )
        
        # Convert to probabilities
        total = sum(final_prefs.values())
        if total > 0:
            weights = [final_prefs[action] / total for action in actions]
        else:
            weights = [0.33, 0.33, 0.34]
            
        return random.choices(actions, weights=weights)[0]
    
    def step(self) -> Dict[str, Any]:
        """Execute one boids step with REAL tool operations."""
        # 1. Observe neighbors
        observations = self.observe_neighbors()
        
        # 2. Apply boids rules  
        sep_prefs = self.apply_separation_rule(observations)
        align_prefs = self.apply_alignment_rule(observations)
        cohes_prefs = self.apply_cohesion_rule(observations)
        
        # 3. Choose action
        action = self.choose_action(sep_prefs, align_prefs, cohes_prefs)
        
        # 4. Execute action
        result = self._execute_action(action, observations)
        
        # 5. Track action
        self.recent_actions.append(action)
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
            
        return {
            'agent_id': self.agent_id,
            'action': action,
            'result': result,
            'observations': observations,
            'tool_count': len([name for name, info in self.tool_registry.get_available_tools().items() 
                             if info['created_by'] == self.agent_id])
        }
    
    def _execute_action(self, action: str, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chosen action."""
        if action == 'create_tool':
            return self._create_real_tool()
        elif action == 'use_tool':
            return self._use_neighbor_tool(observations)
        else:  # rest
            return {'success': True, 'details': 'rested'}
    
    def _create_real_tool(self) -> Dict[str, Any]:
        """Create a REAL computational tool with actual logic."""
        try:
            # Choose tool type based on what hasn't been created much
            available_types = list(self.tool_generators.keys())
            tool_type = random.choice(available_types)
            
            # Generate the actual tool
            tool_spec = self.tool_generators[tool_type]()
            
            # Ensure uniqueness
            base_name = tool_spec['name']
            counter = 1
            while f"{base_name}_{counter}" in self.created_functions:
                counter += 1
            
            final_name = f"{base_name}_{counter}"
            self.created_functions.add(final_name)
            
            # Create the tool
            success = self.tool_registry.create_personal_tool(
                tool_name=final_name,
                description=tool_spec['description'], 
                code=tool_spec['code']
            )
            
            if success:
                # Test the tool
                test_results = self._test_tool(final_name, tool_spec.get('test_cases', []))
                
                return {
                    'success': True,
                    'tool_name': final_name,
                    'tool_type': tool_type,
                    'test_results': test_results,
                    'details': f"Created {tool_type} tool '{final_name}'"
                }
            else:
                return {'success': False, 'details': 'Tool creation failed'}
                
        except Exception as e:
            return {'success': False, 'details': f'Error creating tool: {e}'}
    
    def _generate_math_tool(self) -> Dict[str, Any]:
        """Generate a mathematical computation tool."""
        operations = [
            {
                'name': 'fibonacci_calculator',
                'description': 'Calculates the nth Fibonacci number',
                'code': '''def execute(parameters, context=None):
    """Calculate the nth Fibonacci number"""
    try:
        n = int(parameters.get('n', 10))
        if n <= 0:
            return {"success": False, "result": "n must be positive"}
        
        if n <= 2:
            result = 1
        else:
            a, b = 1, 1
            for i in range(3, n + 1):
                a, b = b, a + b
            result = b
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'n': 5}, {'n': 10}]
            },
            {
                'name': 'prime_checker',
                'description': 'Checks if a number is prime',
                'code': '''def execute(parameters, context=None):
    """Check if a number is prime"""
    try:
        n = int(parameters.get('n', 2))
        if n < 2:
            return {"success": True, "result": False}
        
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return {"success": True, "result": False}
        
        return {"success": True, "result": True}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'n': 17}, {'n': 15}]
            },
            {
                'name': 'factorial_calculator',
                'description': 'Calculates factorial of a number',
                'code': '''def execute(parameters, context=None):
    """Calculate factorial of n"""
    try:
        n = int(parameters.get('n', 5))
        if n < 0:
            return {"success": False, "result": "Factorial undefined for negative numbers"}
        
        result = 1
        for i in range(1, n + 1):
            result *= i
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'n': 5}, {'n': 0}]
            }
        ]
        
        return random.choice(operations)
    
    def _generate_string_tool(self) -> Dict[str, Any]:
        """Generate a string manipulation tool."""
        operations = [
            {
                'name': 'palindrome_checker',
                'description': 'Checks if a string is a palindrome',
                'code': '''def execute(parameters, context=None):
    """Check if string is palindrome"""
    try:
        text = str(parameters.get('text', ''))
        cleaned = ''.join(c.lower() for c in text if c.isalnum())
        is_palindrome = cleaned == cleaned[::-1]
        return {"success": True, "result": is_palindrome}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'text': 'racecar'}, {'text': 'hello'}]
            },
            {
                'name': 'word_counter',
                'description': 'Counts words in text',
                'code': '''def execute(parameters, context=None):
    """Count words in text"""
    try:
        text = str(parameters.get('text', ''))
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        return {"success": True, "result": {"words": word_count, "chars": char_count}}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'text': 'hello world'}, {'text': 'one'}]
            },
            {
                'name': 'text_encoder',
                'description': 'Encodes text using Caesar cipher',
                'code': '''def execute(parameters, context=None):
    """Encode text with Caesar cipher"""
    try:
        text = str(parameters.get('text', ''))
        shift = int(parameters.get('shift', 3))
        
        result = ''
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base + shift) % 26
                result += chr(base + shifted)
            else:
                result += char
                
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'text': 'hello', 'shift': 1}, {'text': 'ABC', 'shift': 3}]
            }
        ]
        
        return random.choice(operations)
    
    def _generate_logic_tool(self) -> Dict[str, Any]:
        """Generate a logical computation tool."""
        operations = [
            {
                'name': 'boolean_evaluator',
                'description': 'Evaluates boolean expressions',
                'code': '''def execute(parameters, context=None):
    """Evaluate boolean expression"""
    try:
        expr = str(parameters.get('expression', 'True'))
        # Simple boolean evaluation
        expr = expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not ')
        
        # Safe evaluation
        allowed_names = {"True": True, "False": False, "and": lambda x, y: x and y, "or": lambda x, y: x or y, "not": lambda x: not x}
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'expression': 'True and False'}, {'expression': 'not False'}]
            }
        ]
        
        return random.choice(operations)
    
    def _generate_data_tool(self) -> Dict[str, Any]:
        """Generate a data processing tool."""
        operations = [
            {
                'name': 'list_sorter',
                'description': 'Sorts a list of numbers',
                'code': '''def execute(parameters, context=None):
    """Sort a list of numbers"""
    try:
        data = parameters.get('data', [])
        if isinstance(data, str):
            data = [float(x.strip()) for x in data.split(',')]
        elif isinstance(data, list):
            data = [float(x) for x in data]
        
        sorted_data = sorted(data)
        return {"success": True, "result": sorted_data}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'data': [3, 1, 4, 1, 5]}, {'data': '9,2,6,5'}]
            },
            {
                'name': 'statistics_calculator',
                'description': 'Calculates basic statistics',
                'code': '''def execute(parameters, context=None):
    """Calculate mean, median, mode of data"""
    try:
        data = parameters.get('data', [])
        if isinstance(data, str):
            data = [float(x.strip()) for x in data.split(',')]
        elif isinstance(data, list):
            data = [float(x) for x in data]
        
        if not data:
            return {"success": False, "result": "No data provided"}
        
        mean = sum(data) / len(data)
        sorted_data = sorted(data)
        n = len(sorted_data)
        median = sorted_data[n//2] if n % 2 == 1 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        
        return {"success": True, "result": {"mean": mean, "median": median, "count": n}}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'data': [1, 2, 3, 4, 5]}, {'data': '10,20,30'}]
            }
        ]
        
        return random.choice(operations)
    
    def _generate_crypto_tool(self) -> Dict[str, Any]:
        """Generate a cryptographic/hash tool."""
        operations = [
            {
                'name': 'simple_hash',
                'description': 'Generates simple hash of input',
                'code': '''def execute(parameters, context=None):
    """Generate simple hash"""
    try:
        text = str(parameters.get('text', ''))
        # Simple hash function
        hash_value = 0
        for char in text:
            hash_value = ((hash_value * 31) + ord(char)) % 1000000
        
        return {"success": True, "result": hash_value}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'text': 'hello'}, {'text': 'world'}]
            }
        ]
        
        return random.choice(operations)
    
    def _generate_analysis_tool(self) -> Dict[str, Any]:
        """Generate an analysis/pattern tool."""
        operations = [
            {
                'name': 'pattern_finder',
                'description': 'Finds patterns in sequences',
                'code': '''def execute(parameters, context=None):
    """Find arithmetic or geometric patterns"""
    try:
        sequence = parameters.get('sequence', [])
        if isinstance(sequence, str):
            sequence = [float(x.strip()) for x in sequence.split(',')]
        
        if len(sequence) < 2:
            return {"success": False, "result": "Need at least 2 numbers"}
        
        # Check arithmetic progression
        diff = sequence[1] - sequence[0]
        is_arithmetic = all(sequence[i] - sequence[i-1] == diff for i in range(1, len(sequence)))
        
        # Check geometric progression
        if sequence[0] != 0:
            ratio = sequence[1] / sequence[0] if sequence[0] != 0 else 0
            is_geometric = all(abs(sequence[i] / sequence[i-1] - ratio) < 0.001 for i in range(1, len(sequence)) if sequence[i-1] != 0)
        else:
            is_geometric = False
        
        result = {"arithmetic": is_arithmetic, "geometric": is_geometric}
        if is_arithmetic:
            result["arithmetic_diff"] = diff
        if is_geometric:
            result["geometric_ratio"] = ratio
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
                'test_cases': [{'sequence': [2, 4, 6, 8]}, {'sequence': [3, 6, 12, 24]}]
            }
        ]
        
        return random.choice(operations)
    
    def _use_neighbor_tool(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Use a tool created by a neighbor."""
        all_tools = self.tool_registry.get_available_tools()
        
        # Filter to neighbor-created tools
        neighbor_tools = {name: info for name, info in all_tools.items() 
                         if info['created_by'] != self.agent_id}
        
        if not neighbor_tools:
            return {'success': False, 'details': 'No neighbor tools available'}
        
        # Choose random neighbor tool
        tool_name = random.choice(list(neighbor_tools.keys()))
        
        # Execute with appropriate test data
        try:
            test_params = self._generate_test_params_for_tool(tool_name)
            result = self.tool_registry.execute_tool(tool_name, test_params)
            return {
                'success': True,
                'used_tool': tool_name,
                'test_params': test_params,
                'result': result,
                'details': f"Used neighbor tool '{tool_name}'"
            }
        except Exception as e:
            return {'success': False, 'details': f'Error using tool {tool_name}: {e}'}
    
    def _generate_test_params_for_tool(self, tool_name: str) -> Dict[str, Any]:
        """Generate appropriate test parameters based on tool name."""
        if 'fibonacci' in tool_name or 'factorial' in tool_name:
            return {'n': random.randint(1, 10)}
        elif 'prime' in tool_name:
            return {'n': random.randint(2, 100)}
        elif 'palindrome' in tool_name:
            return {'text': random.choice(['racecar', 'hello', 'level', 'world'])}
        elif 'word_counter' in tool_name:
            return {'text': 'hello world this is a test'}
        elif 'encoder' in tool_name:
            return {'text': 'hello', 'shift': random.randint(1, 5)}
        elif 'sorter' in tool_name or 'statistics' in tool_name:
            return {'data': [random.randint(1, 100) for _ in range(5)]}
        elif 'hash' in tool_name:
            return {'text': random.choice(['hello', 'world', 'test', 'data'])}
        elif 'pattern' in tool_name:
            return {'sequence': [2, 4, 6, 8, 10]}
        else:
            return {'data': 'test'}
    
    def _test_tool(self, tool_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test the created tool with test cases."""
        results = {'total': len(test_cases), 'passed': 0, 'failed': 0, 'details': []}
        
        for i, test_case in enumerate(test_cases):
            try:
                result = self.tool_registry.execute_tool(tool_name, test_case)
                if result.get('success', False):
                    results['passed'] += 1
                    results['details'].append(f"Test {i+1}: PASS")
                else:
                    results['failed'] += 1
                    results['details'].append(f"Test {i+1}: FAIL - {result.get('result', 'Unknown error')}")
            except Exception as e:
                results['failed'] += 1
                results['details'].append(f"Test {i+1}: ERROR - {e}")
        
        return results
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state for analysis."""
        tools = self.tool_registry.get_available_tools()
        my_tools = {name: info for name, info in tools.items() if info['created_by'] == self.agent_id}
        
        # Analyze tool types
        tool_types = {}
        for name in my_tools.keys():
            tool_type = name.split('_')[0] if '_' in name else 'unknown'
            tool_types[tool_type] = tool_types.get(tool_type, 0) + 1
        
        return {
            'agent_id': self.agent_id,
            'total_tools_created': len(my_tools),
            'total_tools_available': len(tools),
            'tool_types_created': tool_types,
            'recent_actions': self.recent_actions[-5:],
            'boids_weights': {
                'separation': self.separation_weight,
                'alignment': self.alignment_weight, 
                'cohesion': self.cohesion_weight
            },
            'my_tools': list(my_tools.keys())[-3:]  # Show last 3 tools created
        } 