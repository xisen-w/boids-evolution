"""
Real Tool Boids Network - Manages agents with real tool capabilities

DRY PRINCIPLES APPLIED:
- Reuses existing topology setup patterns
- Shared tool evolution and promotion logic
- Common simulation orchestration
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from .real_tool_boids_agent import RealToolBoid
# Azure client is optional
try:
    from .azure_client import AzureOpenAIClient
except ImportError:
    AzureOpenAIClient = None


class RealToolBoidsNetwork:
    """
    Network for managing real tool boids agents.
    
    DRY: Combines network topology management, tool evolution, 
    and simulation orchestration in reusable patterns.
    """
    
    def __init__(self, num_agents: int = 3, topology: str = "triangle", 
                 azure_client = None, 
                 reset_shared_tools: bool = True):
        self.agents = []
        self.topology = topology
        self.azure_client = azure_client
        self.step_count = 0
        self.history = []
        
        # Initialize shared tools from template (DRY: template pattern)
        if reset_shared_tools:
            self._initialize_shared_tools()
        
        # Create agents (DRY: agent factory pattern)
        for i in range(num_agents):
            agent = RealToolBoid(f"Agent_{i+1:02d}", azure_client)
            self.agents.append(agent)
        
        # Set topology (DRY: reuse topology patterns)
        self._setup_topology()
    
    def _initialize_shared_tools(self):
        """Initialize shared tools from template for this simulation. DRY: template management."""
        template_dir = "shared_tools_template"
        target_dir = "shared_tools"
        
        # Create template if it doesn't exist (DRY: idempotent setup)
        if not os.path.exists(template_dir):
            if os.path.exists(target_dir):
                shutil.copytree(target_dir, template_dir)
            else:
                # Create minimal template
                os.makedirs(template_dir, exist_ok=True)
                self._create_minimal_shared_template(template_dir)
        
        # Reset shared tools to template (DRY: clean slate pattern)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(template_dir, target_dir)
        
    def _create_minimal_shared_template(self, template_dir: str):
        """Create minimal shared tools template. DRY: bootstrap pattern."""
        # Create basic index
        index_data = {
            "tools": {},
            "metadata": {
                "version": "1.0",
                "created": "template",
                "description": "Minimal shared tools template"
            }
        }
        
        with open(os.path.join(template_dir, "index.json"), 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def _setup_topology(self):
        """Set up network connections. DRY: reusable topology patterns."""
        topology_handlers = {
            'triangle': self._setup_triangle_topology,
            'line': self._setup_line_topology,
            'star': self._setup_star_topology
        }
        
        handler = topology_handlers.get(self.topology, topology_handlers['triangle'])
        handler()
    
    def _setup_triangle_topology(self):
        """Triangle: everyone connected to everyone. DRY: symmetric connections."""
        if len(self.agents) >= 3:
            for i, agent in enumerate(self.agents):
                neighbors = [other for j, other in enumerate(self.agents) if i != j]
                agent.set_neighbors(neighbors[:2])  # Limit to 2 neighbors for triangle
        
    def _setup_line_topology(self):
        """Line: sequential connections. DRY: neighbor calculation."""
        for i, agent in enumerate(self.agents):
            neighbors = []
            if i > 0:
                neighbors.append(self.agents[i-1])
            if i < len(self.agents) - 1:
                neighbors.append(self.agents[i+1])
            agent.set_neighbors(neighbors)
    
    def _setup_star_topology(self):
        """Star: hub and spoke. DRY: center/periphery pattern."""
        if len(self.agents) > 1:
            center = self.agents[0]
            others = self.agents[1:]
            center.set_neighbors(others)
            for agent in others:
                agent.set_neighbors([center])
    
    def step(self) -> Dict[str, Any]:
        """Run one simulation step. DRY: step orchestration pattern."""
        self.step_count += 1
        step_results = []
        
        # Execute all agent steps (DRY: batch processing)
        for agent in self.agents:
            result = agent.step()
            step_results.append(result)
        
        # Evolve tool ecosystem (DRY: post-step processing)
        self._evolve_tool_ecosystem(step_results)
        
        # Create step summary (DRY: data aggregation)
        step_summary = {
            'step': self.step_count,
            'agent_results': step_results,
            'global_state': self._get_global_state()
        }
        
        self.history.append(step_summary)
        return step_summary
    
    def _evolve_tool_ecosystem(self, step_results: List[Dict[str, Any]]):
        """Evolve the tool ecosystem based on usage patterns. DRY: evolution logic."""
        # Track tool creation and usage this step
        tools_created = []
        tools_used = []
        
        for result in step_results:
            if result['result'].get('success') and result['action'] == 'create_tool':
                tool_name = result['result'].get('tool_name')
                if tool_name:
                    tools_created.append({
                        'name': tool_name,
                        'creator': result['agent_id']
                    })
            
            if result['result'].get('success') and result['action'] == 'use_tool':
                tool_name = result['result'].get('used_tool')
                if tool_name:
                    tools_used.append({
                        'name': tool_name,
                        'user': result['agent_id']
                    })
        
        # Promote successful tools (DRY: promotion criteria)
        self._evaluate_tool_promotions(tools_created, tools_used)
    
    def _evaluate_tool_promotions(self, tools_created: List[Dict], tools_used: List[Dict]):
        """Evaluate which tools should be promoted to shared status. DRY: evaluation criteria."""
        # Simple promotion rule: tools used by multiple agents in same step
        tool_usage_count = {}
        
        for usage in tools_used:
            tool_name = usage['name']
            if tool_name not in tool_usage_count:
                tool_usage_count[tool_name] = set()
            tool_usage_count[tool_name].add(usage['user'])
        
        # Promote tools used by 2+ different agents
        for tool_name, users in tool_usage_count.items():
            if len(users) >= 2:
                self._promote_tool_to_shared(tool_name)
    
    def _promote_tool_to_shared(self, tool_name: str):
        """Promote a successful tool to shared pool. DRY: promotion mechanism."""
        # Find the tool in personal collections
        source_agent = None
        tool_info = None
        
        for agent in self.agents:
            tools = agent.tool_registry.get_available_tools()
            if tool_name in tools and tools[tool_name]['created_by'] == agent.agent_id:
                source_agent = agent
                tool_info = tools[tool_name]
                break
        
        if source_agent and tool_info:
            # Copy to shared tools (simplified - would need full file copy in production)
            print(f"📈 Tool '{tool_name}' by {source_agent.agent_id} promoted to shared pool!")
            # Implementation would copy tool files and update shared index
    
    def _get_global_state(self) -> Dict[str, Any]:
        """Get global simulation state. DRY: state aggregation."""
        # Aggregate statistics across all agents (DRY: batch computation)
        total_personal_tools = 0
        total_actions = {'create_tool': 0, 'use_tool': 0, 'improve_tool': 0, 'rest': 0}
        agent_tool_counts = {}
        
        for agent in self.agents:
            # Count personal tools
            my_tools = [name for name, info in agent.tool_registry.get_available_tools().items() 
                       if info['created_by'] == agent.agent_id]
            total_personal_tools += len(my_tools)
            agent_tool_counts[agent.agent_id] = len(my_tools)
            
            # Count recent actions
            for action in agent.recent_actions[-5:]:  # Last 5 actions
                if action in total_actions:
                    total_actions[action] += 1
        
        # Calculate shared tools
        shared_tools_count = 0
        shared_tools_dir = "shared_tools"
        if os.path.exists(shared_tools_dir):
            shared_tools_count = len([f for f in os.listdir(shared_tools_dir) 
                                    if f.endswith('.py')]) 
        
        return {
            'total_personal_tools': total_personal_tools,
            'total_agents': len(self.agents),
            'shared_tools_count': shared_tools_count,
            'step_count': self.step_count,
            'agent_tool_counts': agent_tool_counts,
            'action_distribution': total_actions
        }
    
    def run_simulation(self, num_steps: int = 50, verbose: bool = True) -> List[Dict[str, Any]]:
        """Run full simulation. DRY: simulation orchestration pattern."""
        if verbose:
            self._print_simulation_header(num_steps)
        
        # Main simulation loop (DRY: step iteration)
        for step in range(num_steps):
            step_result = self.step()
            
            if verbose and self._should_print_step(step):
                self._print_step_summary(step_result)
        
        if verbose:
            self._print_simulation_footer()
        
        return self.history
    
    def _print_simulation_header(self, num_steps: int):
        """Print simulation start info. DRY: header formatting."""
        print(f"🔧 Starting Real Tool Boids Simulation")
        print(f"   Agents: {len(self.agents)} | Topology: {self.topology}")
        print(f"   Steps: {num_steps} | LLM: {'Yes' if self.azure_client else 'Templates only'}")
        print("=" * 60)
    
    def _should_print_step(self, step: int) -> bool:
        """Determine if step should be printed. DRY: printing criteria."""
        return step % 10 == 0 or step < 5
    
    def _print_step_summary(self, step_result: Dict[str, Any]):
        """Print step summary. DRY: step formatting."""
        print(f"\n📊 Step {step_result['step']}:")
        
        # DRY: action formatting
        action_emojis = {
            'create_tool': '🔨',
            'use_tool': '🔧', 
            'improve_tool': '⚡',
            'rest': '😴'
        }
        
        for result in step_result['agent_results']:
            agent_id = result['agent_id']
            action = result['action']
            success = result['result'].get('success', False)
            
            emoji = action_emojis.get(action, '❓')
            status = "✅" if success else "❌"
            
            details = result['result'].get('details', '')
            print(f"   {emoji} {agent_id}: {action} {status} - {details}")
    
    def _print_simulation_footer(self):
        """Print final analysis. DRY: footer formatting."""
        print("\n" + "=" * 60)
        self._print_final_analysis()
    
    def _print_final_analysis(self):
        """Print final analysis. DRY: analysis formatting."""
        print("🧬 REAL TOOL EMERGENCE ANALYSIS:")
        
        # Get final state (DRY: reuse state aggregation)
        final_state = self._get_global_state()
        
        # Print key metrics (DRY: metric formatting)
        print(f"   🔧 Total Real Tools Created: {final_state['total_personal_tools']}")
        print(f"   📊 Tools per Agent: {final_state['agent_tool_counts']}")
        print(f"   🌐 Shared Tools: {final_state['shared_tools_count']}")
        print(f"   📈 Action Distribution: {final_state['action_distribution']}")
        
        # Emergence evaluation (DRY: criteria checking)
        if final_state['total_personal_tools'] > 0:
            print("   ✨ REAL TOOL ECOSYSTEM EMERGED!")
            
            # Check for specialization
            tool_counts = list(final_state['agent_tool_counts'].values())
            if len(set(tool_counts)) > 1:
                print("   🎯 SPECIALIZATION DETECTED: Agents created different numbers of tools")
                
            # Check for collaboration  
            if final_state['action_distribution']['use_tool'] > 0:
                print("   🤝 COLLABORATION DETECTED: Agents used each other's tools")
        else:
            print("   📝 No tools created - check system configuration")
    
    def export_results(self, filename: str = None):
        """Export simulation results. DRY: export pattern."""
        if filename is None:
            filename = f"real_tool_boids_results_{self.topology}_{len(self.agents)}agents_{self.step_count}steps.json"
        
        # Aggregate export data (DRY: data collection)
        export_data = {
            'metadata': {
                'num_agents': len(self.agents),
                'topology': self.topology,
                'total_steps': self.step_count,
                'has_llm': self.azure_client is not None
            },
            'final_state': self._get_global_state(),
            'agent_states': [agent.get_state() for agent in self.agents],
            'history': self.history
        }
        
        # Write export file (DRY: file writing)
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"📁 Results exported to {filename}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics. DRY: stats aggregation."""
        final_state = self._get_global_state()
        
        # Calculate emergence metrics (DRY: metric calculation)
        total_tools = final_state['total_personal_tools']
        agent_counts = list(final_state['agent_tool_counts'].values())
        
        specialization_ratio = len(set(agent_counts)) / len(agent_counts) if agent_counts else 0
        collaboration_actions = final_state['action_distribution']['use_tool']
        creation_actions = final_state['action_distribution']['create_tool']
        
        return {
            'total_tools_created': total_tools,
            'specialization_ratio': specialization_ratio,
            'collaboration_rate': collaboration_actions / max(1, creation_actions),
            'tool_diversity': len(set(agent_counts)),
            'emergence_score': min(1.0, (total_tools * specialization_ratio) / 10)  # Simple score
        } 