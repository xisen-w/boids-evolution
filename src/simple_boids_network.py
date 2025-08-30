"""
Simple Boids Network - Ultra Minimal Network Management

CORE FOCUS: Network topology + simulation orchestration
- Manages agent connections (triangle, line, star topologies)
- Runs pure boids simulation steps
- Tracks emergence patterns

NO CENTRAL COORDINATION - just facilitates local neighbor interactions.
"""

import random
from typing import List, Dict, Any
from .simple_boids_agent import SimpleBoid


class SimpleBoidsNetwork:
    """
    Ultra minimal network for cognitive boids simulation.
    
    NO CENTRAL COORDINATION - just facilitates local interactions
    between agents following the 3 boids rules.
    """
    
    def __init__(self, num_agents: int = 3, topology: str = "triangle"):
        self.agents = []
        self.topology = topology
        self.step_count = 0
        self.history = []
        
        # Create agents
        for i in range(num_agents):
            agent = SimpleBoid(f"Agent_{i+1:02d}")
            self.agents.append(agent)
            
        # Set network topology
        self._setup_topology()
        
    def _setup_topology(self):
        """Set up network connections between agents (who can observe whom)."""
        
        if self.topology == "triangle" and len(self.agents) >= 3:
            # Triangle: everyone connected to everyone (full connectivity)
            for i, agent in enumerate(self.agents):
                neighbors = [a for j, a in enumerate(self.agents) if j != i]
                agent.set_neighbors(neighbors)
            
        elif self.topology == "line":
            # Line: A-B-C (linear chain)
            for i, agent in enumerate(self.agents):
                neighbors = []
                if i > 0:
                    neighbors.append(self.agents[i-1])  # Left neighbor
                if i < len(self.agents) - 1:
                    neighbors.append(self.agents[i+1])  # Right neighbor
                agent.set_neighbors(neighbors)
                
        elif self.topology == "star":
            # Star: center agent connected to all, others only to center
            if len(self.agents) > 1:
                center_agent = self.agents[0]
                peripheral_agents = self.agents[1:]
                
                # Center sees all peripherals
                center_agent.set_neighbors(peripheral_agents)
                
                # Peripherals only see center
                for agent in peripheral_agents:
                    agent.set_neighbors([center_agent])
        else:
            # Default: full connectivity
            for i, agent in enumerate(self.agents):
                neighbors = [a for j, a in enumerate(self.agents) if j != i]
                agent.set_neighbors(neighbors)
                
    def step(self) -> Dict[str, Any]:
        """
        Run one step of the cognitive boids simulation.
        
        Each agent observes neighbors and acts based on 3 simple boids rules.
        NO CENTRAL COORDINATION - pure local interactions!
        """
        self.step_count += 1
        step_results = []
        
        # Each agent acts based on LOCAL observations only
        for agent in self.agents:
            result = agent.step()
            step_results.append(result)
            
        # Track step for analysis (global view for research only)
        step_summary = {
            'step': self.step_count,
            'agent_results': step_results,
            'global_state': self._get_global_state()
        }
        
        self.history.append(step_summary)
        return step_summary
    
    def run_simulation(self, num_steps: int = 50, verbose: bool = True) -> List[Dict[str, Any]]:
        """Run the full boids simulation and return results."""
        
        if verbose:
            print(f"🐦 Simple Boids Simulation Starting")
            print(f"   Agents: {len(self.agents)} | Topology: {self.topology}")
            print(f"   Steps: {num_steps}")
            print(f"   Rules: Separation + Alignment + Cohesion")
            print("\n" + "="*60)
            
        for step in range(num_steps):
            step_result = self.step()
            
            if verbose and (step % 10 == 0 or step < 5):
                self._print_step_summary(step_result)
                
        if verbose:
            print("\n" + "="*60)
            self._print_final_analysis()
            
        return self.history
    
    def _print_step_summary(self, step_result: Dict[str, Any]):
        """Print summary of what happened in this step."""
        step_num = step_result['step']
        print(f"\n📊 Step {step_num}:")
        
        for result in step_result['agent_results']:
            agent_id = result['agent_id']
            action = result['action']
            info = result['info']
            tools_count = result['tools_count']
            
            # Action emojis for visualization
            action_emoji = {
                'build_data': '📊', 'build_logic': '🧠', 
                'build_utility': '🔧', 'build_connector': '🔗',
                'use_tool': '⚡', 'rest': '😴'
            }
            emoji = action_emoji.get(action, '❓')
            
            print(f"   {emoji} {agent_id}: {info} (total tools: {tools_count})")
    
    def _get_global_state(self) -> Dict[str, Any]:
        """Get global state for analysis (not available to agents!)."""
        all_tools = []
        for agent in self.agents:
            all_tools.extend(agent.tools)
        
        # Tool type distribution across all agents
        tool_types = [tool['type'] for tool in all_tools]
        type_counts = {}
        for tool_type in tool_types:
            type_counts[tool_type] = type_counts.get(tool_type, 0) + 1
            
        # Agent specializations (what type does each agent focus on?)
        specializations = {}
        for agent in self.agents:
            agent_tool_types = [t['type'] for t in agent.tools]
            if agent_tool_types:
                # Find most common type for this agent
                agent_type_counts = {}
                for t_type in agent_tool_types:
                    agent_type_counts[t_type] = agent_type_counts.get(t_type, 0) + 1
                primary_type = max(agent_type_counts.items(), key=lambda x: x[1])[0]
                specializations[agent.agent_id] = primary_type
            else:
                specializations[agent.agent_id] = None
            
        return {
            'total_tools': len(all_tools),
            'tool_type_distribution': type_counts,
            'agent_specializations': specializations,
            'agents_with_tools': len([a for a in self.agents if len(a.tools) > 0]),
            'unique_tool_types': len(set(tool_types)) if tool_types else 0
        }
    
    def _print_final_analysis(self):
        """Print final emergence analysis."""
        print("🧬 BOIDS EMERGENCE ANALYSIS:")
        
        final_state = self._get_global_state()
        
        print(f"   📊 Total Tools Created: {final_state['total_tools']}")
        print(f"   🎯 Tool Type Distribution: {final_state['tool_type_distribution']}")
        print(f"   🤖 Agent Specializations: {final_state['agent_specializations']}")
        print(f"   📈 Agents with Tools: {final_state['agents_with_tools']}/{len(self.agents)}")
        print(f"   🌟 Unique Tool Types: {final_state['unique_tool_types']}/4")
        
        # Check for emergent patterns
        specializations = list(final_state['agent_specializations'].values())
        unique_specializations = len(set(spec for spec in specializations if spec))
        
        if unique_specializations > 1:
            print(f"   ✨ SPECIALIZATION EMERGED! {unique_specializations} different niches")
        else:
            print(f"   📝 No clear specialization detected")
            
        # Check tool diversity
        if final_state['unique_tool_types'] >= 3:
            print(f"   🎨 DIVERSITY EMERGED! {final_state['unique_tool_types']} tool types created")
        else:
            print(f"   📝 Limited tool diversity")
            
        # Check for collaboration patterns
        total_use_actions = 0
        for step_data in self.history:
            for result in step_data['agent_results']:
                if result['action'] == 'use_tool':
                    total_use_actions += 1
                    
        if total_use_actions > len(self.agents):
            print(f"   🤝 COLLABORATION EMERGED! {total_use_actions} tool usage events")
        else:
            print(f"   📝 Limited collaboration detected")
            
    def export_results(self, filename: str = "simple_boids_results.json"):
        """Export full simulation results for analysis."""
        import json
        
        export_data = {
            'metadata': {
                'simulation_type': 'simple_boids',
                'num_agents': len(self.agents),
                'topology': self.topology,
                'total_steps': self.step_count
            },
            'final_state': self._get_global_state(),
            'agent_states': [agent.get_state() for agent in self.agents],
            'history': self.history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        print(f"📁 Results exported to {filename}")
        
    def get_network_summary(self) -> Dict[str, Any]:
        """Get current network state summary."""
        return {
            'topology': self.topology,
            'num_agents': len(self.agents),
            'steps_completed': self.step_count,
            'total_tools': sum(len(agent.tools) for agent in self.agents),
            'agent_connections': {
                agent.agent_id: len(agent.neighbors) 
                for agent in self.agents
            }
        } 