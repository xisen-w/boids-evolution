"""
Real Tool Boids Agent - Combines Simple Boids with Real Tool Infrastructure

CORE CONCEPT: 
- Boids rules for decision making (separation, alignment, cohesion)
- Real tool creation, testing, and usage (from enhanced_tools)
- No fake tool types - actual executable Python functions
"""

import os
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from .enhanced_tools import EnhancedToolRegistry


class RealToolBoid:
    """
    Boids agent that creates, tests, and uses real executable tools.
    
    Combines:
    - 3 Boids Rules (separation, alignment, cohesion) 
    - Real tool creation (Python functions with tests)
    - Tool usage tracking and evolution
    """
    
    def __init__(self, agent_id: str, azure_client=None):
        self.agent_id = agent_id
        self.azure_client = azure_client
        
        # Real tool registry (DRY: reuse existing enhanced system)
        self.tool_registry = EnhancedToolRegistry(agent_id)
        
        # Boids state
        self.neighbors = []
        self.recent_actions = []
        
        # Boids rule weights (ready for genetics later)
        self.separation_weight = 0.4
        self.alignment_weight = 0.3  
        self.cohesion_weight = 0.3
        
        # Tool creation templates (DRY: reusable patterns)
        self.tool_templates = {
            'math': '''def execute(parameters, context=None):
    """Mathematical operation tool"""
    try:
        a = float(parameters.get('a', 0))
        b = float(parameters.get('b', 0))
        op = parameters.get('operation', 'add')
        
        if op == 'add':
            result = a + b
        elif op == 'multiply':
            result = a * b
        else:
            result = a + b  # fallback
            
        return {"success": True, "result": str(result)}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
        
            'data': '''def execute(parameters, context=None):
    """Data processing tool"""
    try:
        data = parameters.get('data', '')
        action = parameters.get('action', 'process')
        
        if action == 'uppercase':
            result = str(data).upper()
        elif action == 'reverse':
            result = str(data)[::-1]
        else:
            result = f"processed: {data}"
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}''',
        
            'utility': '''def execute(parameters, context=None):
    """Utility function tool"""
    try:
        import random
        from datetime import datetime
        
        task = parameters.get('task', 'help')
        
        if task == 'timestamp':
            result = datetime.now().isoformat()
        elif task == 'random':
            result = str(random.randint(1, 100))
        else:
            result = f"utility task: {task}"
            
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}'''
        }
        
    def set_neighbors(self, neighbors: List['RealToolBoid']):
        """Set network neighbors for boids observations."""
        self.neighbors = neighbors
        
    def observe_neighbors(self) -> Dict[str, Any]:
        """Observe what neighbors have created and done."""
        neighbor_tools = []
        neighbor_actions = []
        
        for neighbor in self.neighbors:
            # Get neighbor's personal tool names (real tools from registry)
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
        """
        SEPARATION: Avoid creating tools similar to what neighbors just created.
        
        Returns preferences for different actions.
        """
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0, 
            'improve_tool': 1.0,
            'rest': 1.0
        }
        
        # Count what neighbors recently created
        recent_neighbor_tools = []
        for neighbor_tools in observations['neighbor_tools']:
            recent_neighbor_tools.extend(neighbor_tools[-2:])  # Last 2 tools per neighbor
            
        # If neighbors created many tools recently, prefer other actions
        if len(recent_neighbor_tools) >= 2:
            preferences['create_tool'] *= 0.3  # Strongly avoid creating more
            preferences['use_tool'] *= 1.5     # Prefer using instead
            
        return preferences
    
    def apply_alignment_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """
        ALIGNMENT: Copy strategies of neighbors who have more tools (success).
        """
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0,
            'improve_tool': 1.0, 
            'rest': 1.0
        }
        
        # Find most successful neighbor (most tools)
        my_tool_count = len([name for name, info in self.tool_registry.get_available_tools().items() 
                           if info['created_by'] == self.agent_id])
        successful_neighbor_actions = []
        
        for i, neighbor_tools in enumerate(observations['neighbor_tools']):
            if len(neighbor_tools) > my_tool_count:
                # This neighbor is more successful, copy their recent actions
                neighbor_actions = observations['neighbor_actions'][i]
                successful_neighbor_actions.extend(neighbor_actions)
        
        # Boost preferences for actions taken by successful neighbors
        for action in successful_neighbor_actions:
            if action in preferences:
                preferences[action] *= 1.5
                
        return preferences
    
    def apply_cohesion_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """
        COHESION: Use and build upon neighbors' tools.
        """
        preferences = {
            'create_tool': 1.0,
            'use_tool': 1.0,
            'improve_tool': 1.0,
            'rest': 1.0
        }
        
        # Count available neighbor tools
        total_neighbor_tools = sum(len(tools) for tools in observations['neighbor_tools'])
        
        if total_neighbor_tools > 0:
            preferences['use_tool'] *= 2.0      # Prefer using neighbor tools
            preferences['improve_tool'] *= 1.5  # Prefer improving on them
        else:
            preferences['create_tool'] *= 1.5   # Create if no tools to use
            
        return preferences
    
    def choose_action(self, sep_prefs: Dict[str, float], align_prefs: Dict[str, float], cohes_prefs: Dict[str, float]) -> str:
        """Combine boids rule preferences to choose an action. DRY: reusable weighted choice logic."""
        actions = ['create_tool', 'use_tool', 'improve_tool', 'rest']
        
        # Weighted combination of preferences
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
            weights = [0.25, 0.25, 0.25, 0.25]  # Equal fallback
            
        return random.choices(actions, weights=weights)[0]
    
    def step(self) -> Dict[str, Any]:
        """Execute one boids step with real tool operations."""
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
        
        # 5. Track action (DRY: simple state management)
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
        """Execute the chosen action with real tool operations. DRY: dispatch pattern."""
        if action == 'create_tool':
            return self._create_new_tool()
        elif action == 'use_tool':
            return self._use_neighbor_tool(observations)
        elif action == 'improve_tool':
            return self._improve_existing_tool(observations)
        else:  # rest
            return {'success': True, 'details': 'rested'}
    
    def _create_new_tool(self) -> Dict[str, Any]:
        """Create a new tool using templates (LLM removed for simplicity)."""
        try:
            # Generate tool idea from template
            tool_idea = self._generate_tool_from_template()
            
            # Create the actual tool file and metadata (DRY: reuse enhanced_tools)
            success = self.tool_registry.create_personal_tool(
                tool_name=tool_idea['name'],
                description=tool_idea['description'], 
                code=tool_idea['code']
            )
            
            if success:
                # Generate and run test cases
                test_results = self._generate_and_run_tests(tool_idea['name'])
                
                return {
                    'success': True,
                    'tool_name': tool_idea['name'],
                    'test_results': test_results,
                    'details': f"Created tool '{tool_idea['name']}'"
                }
            else:
                return {'success': False, 'details': 'Tool creation failed'}
                
        except Exception as e:
            return {'success': False, 'details': f'Error creating tool: {e}'}
    
    def _use_neighbor_tool(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Use a tool created by a neighbor. DRY: reuse tool_registry execution."""
        # Get all available tools (DRY: use existing registry method)
        all_tools = self.tool_registry.get_available_tools()
        
        # Filter to neighbor-created tools
        neighbor_tools = {name: info for name, info in all_tools.items() 
                         if info['created_by'] != self.agent_id}
        
        if not neighbor_tools:
            return {'success': False, 'details': 'No neighbor tools available'}
        
        # Choose random neighbor tool
        tool_name = random.choice(list(neighbor_tools.keys()))
        
        # Execute it with sample parameters (DRY: reuse registry execution)
        try:
            result = self.tool_registry.execute_tool(tool_name, {'data': 'test_input'})
            return {
                'success': True,
                'used_tool': tool_name,
                'result': result,
                'details': f"Used neighbor tool '{tool_name}'"
            }
        except Exception as e:
            return {'success': False, 'details': f'Error using tool {tool_name}: {e}'}
    
    def _improve_existing_tool(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """Improve an existing tool by adding functionality."""
        # Get available tools (DRY: reuse registry)
        all_tools = list(self.tool_registry.get_available_tools().keys())
        
        if not all_tools:
            return self._create_new_tool()  # Fallback to creation
        
        base_tool = random.choice(all_tools)
        improved_name = f"improved_{base_tool}_{random.randint(1,999)}"
        
        # Simple improvement: create enhanced version (DRY: template pattern)
        improved_code = f'''def execute(parameters, context=None):
    """Improved version of {base_tool}"""
    try:
        # Enhanced functionality
        if context:
            # Can call original tool if context available
            original_result = context.call_tool("{base_tool}", parameters)
            return {{"success": True, "result": f"Enhanced: {{original_result.get('result', '')}}"}}
        return {{"success": True, "result": "Enhanced standalone execution"}}
    except Exception as e:
        return {{"success": False, "result": f"Error: {{e}}"}}'''
        
        # DRY: reuse tool creation method
        success = self.tool_registry.create_personal_tool(
            tool_name=improved_name,
            description=f"Enhanced version of {base_tool}",
            code=improved_code
        )
        
        if success:
            return {
                'success': True,
                'improved_tool': improved_name,
                'base_tool': base_tool,
                'details': f"Improved {base_tool} → {improved_name}"
            }
        else:
            return {'success': False, 'details': 'Tool improvement failed'}
    
    def _generate_tool_from_template(self) -> Dict[str, Any]:
        """Generate tool from predefined templates. DRY: template selection."""
        template_type = random.choice(list(self.tool_templates.keys()))
        tool_id = random.randint(1000, 9999)
        
        return {
            'name': f"{template_type}_tool_{tool_id}",
            'description': f"A {template_type} processing tool created by {self.agent_id}",
            'code': self.tool_templates[template_type]
        }
    
    def _generate_and_run_tests(self, tool_name: str) -> Dict[str, Any]:
        """Generate and run unit tests for the tool. DRY: test execution pattern."""
        # DRY: reusable test case templates
        test_cases = [
            {
                'name': 'basic_execution',
                'inputs': {'data': 'test_input'},
                'expected_success': True
            },
            {
                'name': 'empty_params',
                'inputs': {},
                'expected_success': True  # Should handle gracefully
            }
        ]
        
        results = {'total': len(test_cases), 'passed': 0, 'failed': 0, 'details': []}
        
        for test_case in test_cases:
            try:
                # DRY: reuse registry execution
                result = self.tool_registry.execute_tool(tool_name, test_case['inputs'])
                
                if result.get('success') == test_case['expected_success']:
                    results['passed'] += 1
                    results['details'].append(f"{test_case['name']}: PASS")
                else:
                    results['failed'] += 1
                    results['details'].append(f"{test_case['name']}: FAIL - unexpected success value")
                    
            except Exception as e:
                results['failed'] += 1
                results['details'].append(f"{test_case['name']}: ERROR - {e}")
        
        return results
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state for analysis. DRY: state aggregation pattern."""
        tools = self.tool_registry.get_available_tools()
        my_tools = {name: info for name, info in tools.items() if info['created_by'] == self.agent_id}
        
        return {
            'agent_id': self.agent_id,
            'total_tools_created': len(my_tools),
            'total_tools_available': len(tools),
            'recent_actions': self.recent_actions[-5:],
            'boids_weights': {
                'separation': self.separation_weight,
                'alignment': self.alignment_weight, 
                'cohesion': self.cohesion_weight
            },
            'my_tools': list(my_tools.keys())
        } 