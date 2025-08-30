"""
Proper Tool Boids Network - Uses agents that create REAL computational tools

IMPROVEMENTS:
- Real mathematical and computational functions
- Diverse tool types (math, string, logic, data, crypto, analysis)
- Meaningful complexity progression
- Actual algorithmic content, not wrapper functions
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from .proper_tool_boids_agent import ProperToolBoid


class ProperToolBoidsNetwork:
    """
    Network for managing proper tool boids agents that create real computational tools.
    """
    
    def __init__(self, num_agents: int = 3, topology: str = "triangle", 
                 azure_client = None, reset_shared_tools: bool = True):
        self.agents = []
        self.topology = topology
        self.azure_client = azure_client
        self.step_count = 0
        self.history = []
        
        # Initialize clean environment
        if reset_shared_tools:
            self._initialize_clean_environment()
        
        # Create agents
        for i in range(num_agents):
            agent = ProperToolBoid(f"Agent_{i+1:02d}", azure_client)
            self.agents.append(agent)
        
        # Set topology
        self._setup_topology()
    
    def _initialize_clean_environment(self):
        """Initialize a clean environment for real tool creation."""
        # Clean up any existing agent directories
        if os.path.exists("personal_tools"):
            for item in os.listdir("personal_tools"):
                if item.startswith("Agent_"):
                    shutil.rmtree(os.path.join("personal_tools", item), ignore_errors=True)
        
        # Ensure shared_tools exists
        if not os.path.exists("shared_tools"):
            os.makedirs("shared_tools", exist_ok=True)
    
    def _setup_topology(self):
        """Set up network connections."""
        if self.topology == "triangle" and len(self.agents) >= 3:
            # Triangle: everyone connected to everyone (limited to 3 for true triangle)
            for i in range(min(3, len(self.agents))):
                neighbors = [self.agents[j] for j in range(min(3, len(self.agents))) if i != j]
                self.agents[i].set_neighbors(neighbors)
                
        elif self.topology == "line":
            # Line: sequential connections
            for i, agent in enumerate(self.agents):
                neighbors = []
                if i > 0:
                    neighbors.append(self.agents[i-1])
                if i < len(self.agents) - 1:
                    neighbors.append(self.agents[i+1])
                agent.set_neighbors(neighbors)
                
        elif self.topology == "star":
            # Star: hub and spoke
            if len(self.agents) > 1:
                center = self.agents[0]
                others = self.agents[1:]
                center.set_neighbors(others)
                for agent in others:
                    agent.set_neighbors([center])
    
    def step(self) -> Dict[str, Any]:
        """Run one simulation step."""
        self.step_count += 1
        step_results = []
        
        # Execute all agent steps
        for agent in self.agents:
            result = agent.step()
            step_results.append(result)
        
        # Analyze tools created this step
        tools_created_this_step = []
        for result in step_results:
            if result['result'].get('success') and result['action'] == 'create_tool':
                tools_created_this_step.append({
                    'agent': result['agent_id'],
                    'tool_name': result['result'].get('tool_name'),
                    'tool_type': result['result'].get('tool_type'),
                    'test_results': result['result'].get('test_results')
                })
        
        step_summary = {
            'step': self.step_count,
            'agent_results': step_results,
            'tools_created_this_step': tools_created_this_step,
            'global_state': self._get_global_state()
        }
        
        self.history.append(step_summary)
        return step_summary
    
    def _get_global_state(self) -> Dict[str, Any]:
        """Get global simulation state."""
        total_personal_tools = 0
        tool_types_created = {}
        agent_tool_counts = {}
        action_distribution = {'create_tool': 0, 'use_tool': 0, 'rest': 0}
        
        for agent in self.agents:
            # Count personal tools
            tools = agent.tool_registry.get_available_tools()
            my_tools = [name for name, info in tools.items() if info['created_by'] == agent.agent_id]
            total_personal_tools += len(my_tools)
            agent_tool_counts[agent.agent_id] = len(my_tools)
            
            # Analyze tool types
            for tool_name in my_tools:
                tool_type = tool_name.split('_')[0] if '_' in tool_name else 'unknown'
                tool_types_created[tool_type] = tool_types_created.get(tool_type, 0) + 1
            
            # Count recent actions
            for action in agent.recent_actions[-5:]:
                if action in action_distribution:
                    action_distribution[action] += 1
        
        # Calculate shared tools
        shared_tools_count = len([f for f in os.listdir("shared_tools") if f.endswith('.py')]) if os.path.exists("shared_tools") else 0
        
        return {
            'total_personal_tools': total_personal_tools,
            'total_agents': len(self.agents),
            'shared_tools_count': shared_tools_count,
            'step_count': self.step_count,
            'agent_tool_counts': agent_tool_counts,
            'tool_types_created': tool_types_created,
            'action_distribution': action_distribution
        }
    
    def run_simulation(self, num_steps: int = 30, verbose: bool = True) -> List[Dict[str, Any]]:
        """Run full simulation."""
        if verbose:
            self._print_simulation_header(num_steps)
        
        for step in range(num_steps):
            step_result = self.step()
            
            if verbose and self._should_print_step(step):
                self._print_step_summary(step_result)
        
        if verbose:
            self._print_simulation_footer()
        
        return self.history
    
    def _print_simulation_header(self, num_steps: int):
        """Print simulation start info."""
        print(f"🧮 Starting PROPER Tool Boids Simulation")
        print(f"   🎯 REAL COMPUTATIONAL TOOLS: Math, String, Logic, Data, Crypto, Analysis")
        print(f"   👥 Agents: {len(self.agents)} | Topology: {self.topology}")
        print(f"   🔄 Steps: {num_steps}")
        print("=" * 70)
    
    def _should_print_step(self, step: int) -> bool:
        """Determine if step should be printed."""
        return step % 5 == 0 or step < 3
    
    def _print_step_summary(self, step_result: Dict[str, Any]):
        """Print step summary."""
        print(f"\n📊 Step {step_result['step']}:")
        
        # Action summary
        action_emojis = {
            'create_tool': '🔨',
            'use_tool': '🔧', 
            'rest': '😴'
        }
        
        for result in step_result['agent_results']:
            agent_id = result['agent_id']
            action = result['action']
            success = result['result'].get('success', False)
            
            emoji = action_emojis.get(action, '❓')
            status = "✅" if success else "❌"
            
            details = result['result'].get('details', '')
            if action == 'create_tool' and success:
                tool_type = result['result'].get('tool_type', 'unknown')
                tool_name = result['result'].get('tool_name', 'unknown')
                test_results = result['result'].get('test_results', {})
                passed = test_results.get('passed', 0)
                total = test_results.get('total', 0)
                details = f"Created {tool_type} tool '{tool_name}' (tests: {passed}/{total})"
            elif action == 'use_tool' and success:
                used_tool = result['result'].get('used_tool', 'unknown')
                tool_result = result['result'].get('result', {})
                details = f"Used '{used_tool}' → {tool_result.get('result', 'N/A')}"
            
            print(f"   {emoji} {agent_id}: {action} {status} - {details}")
        
        # Tools created this step
        if step_result['tools_created_this_step']:
            print(f"   🆕 New tools this step: {len(step_result['tools_created_this_step'])}")
    
    def _print_simulation_footer(self):
        """Print final analysis."""
        print("\n" + "=" * 70)
        self._print_final_analysis()
    
    def _print_final_analysis(self):
        """Print final analysis."""
        print("🧬 REAL COMPUTATIONAL TOOL EMERGENCE ANALYSIS:")
        
        final_state = self._get_global_state()
        
        print(f"   🔧 Total Computational Tools Created: {final_state['total_personal_tools']}")
        print(f"   📊 Tools per Agent: {final_state['agent_tool_counts']}")
        print(f"   🎭 Tool Types Created: {final_state['tool_types_created']}")
        print(f"   📈 Action Distribution: {final_state['action_distribution']}")
        
        # Analyze diversity
        tool_types = final_state['tool_types_created']
        type_diversity = len(tool_types)
        
        if final_state['total_personal_tools'] > 0:
            print("   ✨ REAL COMPUTATIONAL ECOSYSTEM EMERGED!")
            
            if type_diversity >= 3:
                print(f"   🌈 HIGH DIVERSITY: {type_diversity} different computational domains")
                
            # Check for specialization
            agent_counts = list(final_state['agent_tool_counts'].values())
            if len(set(agent_counts)) > 1:
                print("   🎯 SPECIALIZATION DETECTED: Agents show different productivity levels")
                
            # Check for collaboration  
            if final_state['action_distribution']['use_tool'] > 0:
                print("   🤝 COLLABORATION DETECTED: Agents used each other's tools")
                
            # Check tool type distribution
            if tool_types:
                most_common_type = max(tool_types.items(), key=lambda x: x[1])
                print(f"   📈 Most Popular Domain: {most_common_type[0]} ({most_common_type[1]} tools)")
                
        else:
            print("   📝 No tools created - check system configuration")
        
        print(f"\n🔍 Check personal_tools/Agent_XX/ directories for real computational tool files")
    
    def export_results(self, filename: str = None):
        """Export simulation results."""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proper_tools_{self.topology}_{len(self.agents)}agents_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'simulation_type': 'proper_computational_tools',
                'num_agents': len(self.agents),
                'topology': self.topology,
                'total_steps': self.step_count,
                'has_llm': self.azure_client is not None
            },
            'final_state': self._get_global_state(),
            'agent_states': [agent.get_state() for agent in self.agents],
            'history': self.history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"📁 Results exported to {filename}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        final_state = self._get_global_state()
        
        total_tools = final_state['total_personal_tools']
        agent_counts = list(final_state['agent_tool_counts'].values())
        tool_types = final_state['tool_types_created']
        
        # Calculate metrics
        specialization_ratio = len(set(agent_counts)) / len(agent_counts) if agent_counts else 0
        collaboration_actions = final_state['action_distribution']['use_tool']
        creation_actions = final_state['action_distribution']['create_tool']
        type_diversity = len(tool_types) / 6.0  # 6 is max tool types we have
        
        return {
            'total_tools_created': total_tools,
            'specialization_ratio': specialization_ratio,
            'collaboration_rate': collaboration_actions / max(1, creation_actions),
            'tool_type_diversity': type_diversity,
            'computational_domains': list(tool_types.keys()),
            'emergence_score': min(1.0, (total_tools * specialization_ratio * type_diversity) / 10)
        } 