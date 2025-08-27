"""
Tool Execution Context - Enables recursive tool calling and reward propagation.

This is the key innovation that allows tools to call other tools, creating
a composable ecosystem where agents are rewarded for creating useful building blocks.
"""
from typing import Dict, Any, Optional, List, Set
from datetime import datetime


class ToolExecutionContext:
    """
    Context for tool execution that enables:
    1. Recursive tool calling (tools can call other tools)
    2. Reward propagation (tool creators get utility rewards)
    3. Circular dependency detection
    4. Call stack tracking for debugging
    """
    
    def __init__(self, tool_registry, calling_agent_id: str, call_stack: List[str] = None, max_depth: int = 5):
        self.tool_registry = tool_registry
        self.calling_agent_id = calling_agent_id
        self.call_stack = call_stack or []
        self.max_depth = max_depth
        self.utility_rewards: Dict[str, int] = {}  # agent_id -> reward points
        self.tool_usage_count: Dict[str, int] = {}  # tool_name -> usage count
        self.execution_trace: List[Dict[str, Any]] = []  # Detailed execution log
        
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call another tool from within a tool execution.
        
        This is the core mechanism that enables tool composition and creates
        the recursive ecosystem where tools build upon other tools.
        """
        # Check recursion depth
        if len(self.call_stack) >= self.max_depth:
            return {
                'success': False,
                'result': f'Maximum recursion depth ({self.max_depth}) reached',
                'energy_gain': 0,
                'error': 'MAX_DEPTH_REACHED'
            }
        
        # Check for circular dependencies
        if tool_name in self.call_stack:
            return {
                'success': False,
                'result': f'Circular dependency detected: {" -> ".join(self.call_stack + [tool_name])}',
                'energy_gain': 0,
                'error': 'CIRCULAR_DEPENDENCY'
            }
        
        # Check if tool exists
        if not self.tool_registry.get_tool(tool_name):
            return {
                'success': False,
                'result': f'Tool "{tool_name}" not found in registry',
                'energy_gain': 0,
                'error': 'TOOL_NOT_FOUND'
            }
        
        # Create child context for recursive execution
        child_context = self.create_child_context(tool_name)
        
        # Log the tool call
        call_info = {
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'parameters': parameters,
            'calling_agent': self.calling_agent_id,
            'call_depth': len(self.call_stack),
            'call_stack': self.call_stack.copy()
        }
        
        try:
            # Execute the tool with the child context
            result = self.tool_registry.execute_tool_with_context(tool_name, parameters, child_context)
            
            # Track successful tool usage
            if result.get('success', False):
                self.tool_usage_count[tool_name] = self.tool_usage_count.get(tool_name, 0) + 1
                
                # Distribute utility rewards
                self._distribute_utility_reward(tool_name, result.get('energy_gain', 0))
                
                # Merge child context rewards into parent
                self._merge_child_rewards(child_context)
            
            # Log the result
            call_info.update({
                'result': result,
                'success': result.get('success', False),
                'execution_time': datetime.now().isoformat()
            })
            self.execution_trace.append(call_info)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'result': f'Error executing tool "{tool_name}": {str(e)}',
                'energy_gain': 0,
                'error': 'EXECUTION_ERROR'
            }
            
            call_info.update({
                'result': error_result,
                'success': False,
                'error': str(e),
                'execution_time': datetime.now().isoformat()
            })
            self.execution_trace.append(call_info)
            
            return error_result
    
    def create_child_context(self, tool_name: str) -> 'ToolExecutionContext':
        """Create a child context for recursive tool execution."""
        child_call_stack = self.call_stack + [tool_name]
        return ToolExecutionContext(
            tool_registry=self.tool_registry,
            calling_agent_id=self.calling_agent_id,
            call_stack=child_call_stack,
            max_depth=self.max_depth
        )
    
    def _distribute_utility_reward(self, tool_name: str, primary_energy: int):
        """
        Distribute utility rewards to tool creators.
        
        When a tool is used by another tool, the creator gets a utility reward.
        This creates incentive for building useful, reusable tools.
        """
        tool_info = self.tool_registry.get_tool_info(tool_name)
        if not tool_info:
            return
        
        tool_creator = tool_info.get('created_by', 'system')
        
        # Don't reward self-usage
        if tool_creator == self.calling_agent_id or tool_creator == 'system':
            return
        
        # Calculate utility reward (smaller than primary reward)
        utility_reward = max(1, primary_energy // 3)  # 1/3 of primary reward, minimum 1
        
        # Add to utility rewards
        self.utility_rewards[tool_creator] = self.utility_rewards.get(tool_creator, 0) + utility_reward
        
        # Log the utility reward
        print(f"💰 Utility reward: {tool_creator} gets +{utility_reward} for '{tool_name}' usage")
    
    def _merge_child_rewards(self, child_context: 'ToolExecutionContext'):
        """Merge utility rewards from child context executions."""
        for agent_id, reward in child_context.utility_rewards.items():
            self.utility_rewards[agent_id] = self.utility_rewards.get(agent_id, 0) + reward
        
        # Merge tool usage counts
        for tool_name, count in child_context.tool_usage_count.items():
            self.tool_usage_count[tool_name] = self.tool_usage_count.get(tool_name, 0) + count
        
        # Merge execution traces
        self.execution_trace.extend(child_context.execution_trace)
    
    def get_total_rewards(self) -> Dict[str, int]:
        """Get total rewards to be distributed to all agents."""
        return self.utility_rewards.copy()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution including all tool calls and rewards."""
        return {
            'calling_agent': self.calling_agent_id,
            'call_stack': self.call_stack,
            'tools_used': list(self.tool_usage_count.keys()),
            'total_tool_calls': sum(self.tool_usage_count.values()),
            'utility_rewards': self.utility_rewards,
            'execution_trace': self.execution_trace,
            'call_depth': len(self.call_stack)
        }
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Build a dependency graph of tool calls from the execution trace."""
        dependencies = {}
        
        for trace in self.execution_trace:
            caller = trace.get('call_stack', [])[-1] if trace.get('call_stack') else 'root'
            tool_name = trace.get('tool_name')
            
            if caller not in dependencies:
                dependencies[caller] = []
            
            if tool_name and tool_name not in dependencies[caller]:
                dependencies[caller].append(tool_name)
        
        return dependencies
    
    def is_recursive_call(self, tool_name: str) -> bool:
        """Check if calling this tool would create recursion."""
        return tool_name in self.call_stack
    
    def get_call_depth(self) -> int:
        """Get current call depth."""
        return len(self.call_stack)
    
    def __str__(self) -> str:
        return f"ToolExecutionContext(agent={self.calling_agent_id}, depth={len(self.call_stack)}, stack={' -> '.join(self.call_stack)})" 