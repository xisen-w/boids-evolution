"""
Cognitive Boids Algorithm for AI Agent Collaboration

Adapts Craig Reynolds' Boids flocking algorithm to create emergent 
collaborative intelligence in AI agent societies.

Three Rules:
1. SEPARATION: Avoid redundant tool proposals (niche finding)
2. ALIGNMENT: Build tools that complement ecosystem  
3. COHESION: Gravitate toward successful collaborators
"""

from typing import Dict, List, Any, Tuple
import numpy as np
from collections import defaultdict


class CognitiveBoids:
    """
    Implements Cognitive Boids algorithm for AI agent collaboration.
    
    Transforms spatial flocking rules into cognitive collaboration rules
    to generate emergent tool ecosystems and agent specialization.
    """
    
    def __init__(self, separation_weight=0.3, alignment_weight=0.4, cohesion_weight=0.3):
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight  
        self.cohesion_weight = cohesion_weight
        
        # Track agent behavior patterns
        self.agent_roles = defaultdict(list)  # Track agent role evolution
        self.tool_lineages = defaultdict(list)  # Track tool dependency chains
        self.collaboration_network = defaultdict(set)  # Track agent connections
        
    def compute_cognitive_forces(self, agent_id: str, agents: List[Any], 
                                tool_marketplace: Any, communication_board: Any) -> Dict[str, float]:
        """
        Compute the three cognitive boids forces for an agent.
        
        Returns action recommendations weighted by force strength.
        """
        
        # Get local environment information
        neighbors = self._get_neighbors(agent_id, agents, communication_board)
        tool_landscape = self._analyze_tool_landscape(tool_marketplace)
        agent_reputation = self._get_agent_reputation(agent_id, tool_marketplace)
        
        # Compute three cognitive forces
        separation_force = self._compute_separation_force(agent_id, tool_landscape)
        alignment_force = self._compute_alignment_force(agent_id, neighbors, tool_landscape)  
        cohesion_force = self._compute_cohesion_force(agent_id, neighbors, agent_reputation)
        
        # Weight and combine forces
        total_force = {
            'propose_new_tool': (
                separation_force['propose_new_tool'] * self.separation_weight +
                alignment_force['propose_new_tool'] * self.alignment_weight +
                cohesion_force['propose_new_tool'] * self.cohesion_weight
            ),
            'support_proposal': (
                separation_force['support_proposal'] * self.separation_weight +
                alignment_force['support_proposal'] * self.alignment_weight +
                cohesion_force['support_proposal'] * self.cohesion_weight
            ),
            'build_tool': (
                separation_force['build_tool'] * self.separation_weight +
                alignment_force['build_tool'] * self.alignment_weight +
                cohesion_force['build_tool'] * self.cohesion_weight
            ),
            'communicate': (
                separation_force['communicate'] * self.separation_weight +
                alignment_force['communicate'] * self.alignment_weight +
                cohesion_force['communicate'] * self.cohesion_weight
            )
        }
        
        return total_force
    
    def _compute_separation_force(self, agent_id: str, tool_landscape: Dict) -> Dict[str, float]:
        """
        SEPARATION: Avoid redundant tool proposals (niche finding).
        
        Agents are repelled from creating tools too similar to existing ones,
        encouraging exploration of new niches and avoiding redundancy.
        """
        forces = {'propose_new_tool': 0.5, 'support_proposal': 0.3, 'build_tool': 0.2, 'communicate': 0.1}
        
        # Analyze tool density in different categories
        tool_categories = self._categorize_tools(tool_landscape)
        oversaturated_categories = [cat for cat, count in tool_categories.items() if count > 3]
        
        # Strong separation force if many similar tools exist
        if len(oversaturated_categories) > 2:
            forces['propose_new_tool'] = 0.8  # Strong drive to find new niches
            forces['support_proposal'] = 0.1  # Avoid supporting redundant proposals
        
        return forces
    
    def _compute_alignment_force(self, agent_id: str, neighbors: List[str], 
                               tool_landscape: Dict) -> Dict[str, float]:
        """
        ALIGNMENT: Build tools that complement ecosystem.
        
        Agents align their tool-building with community needs and 
        existing tool gaps, creating coherent tool ecosystems.
        """
        forces = {'propose_new_tool': 0.3, 'support_proposal': 0.4, 'build_tool': 0.5, 'communicate': 0.3}
        
        # Identify ecosystem gaps and complementary opportunities
        ecosystem_gaps = self._identify_ecosystem_gaps(tool_landscape)
        complementary_opportunities = self._find_complementary_tools(tool_landscape)
        
        # Strong alignment toward filling gaps and building complementary tools
        if ecosystem_gaps:
            forces['propose_new_tool'] = 0.7  # Propose tools to fill gaps
            forces['build_tool'] = 0.8  # Build tools that complete the ecosystem
            
        if complementary_opportunities:
            forces['support_proposal'] = 0.7  # Support proposals that complement existing tools
            
        return forces
    
    def _compute_cohesion_force(self, agent_id: str, neighbors: List[str], 
                              agent_reputation: Dict) -> Dict[str, float]:
        """
        COHESION: Gravitate toward successful collaborators.
        
        Agents are attracted to successful tool creators and form 
        collaboration clusters around productive agents.
        """
        forces = {'propose_new_tool': 0.2, 'support_proposal': 0.6, 'build_tool': 0.4, 'communicate': 0.8}
        
        # Find highly successful agents (high reputation/energy)
        successful_agents = [agent for agent, rep in agent_reputation.items() 
                           if rep.get('reputation_score', 0) > 20]
        
        # If there are successful agents, gravitate toward them
        if successful_agents:
            forces['support_proposal'] = 0.8  # Support proposals from successful agents
            forces['communicate'] = 0.9  # Communicate with successful agents
            forces['build_tool'] = 0.6  # Build tools proposed by successful agents
            
        return forces
    
    def _get_neighbors(self, agent_id: str, agents: List[Any], 
                      communication_board: Any) -> List[str]:
        """Get agents that have communicated with this agent recently."""
        neighbors = []
        messages = communication_board.get_messages_for_agent(agent_id)
        
        for msg in messages[-10:]:  # Recent messages
            if msg.sender != agent_id:
                neighbors.append(msg.sender)
            if msg.recipient == agent_id:
                neighbors.append(msg.sender)
                
        return list(set(neighbors))
    
    def _analyze_tool_landscape(self, tool_marketplace: Any) -> Dict:
        """Analyze current tool ecosystem for patterns and gaps."""
        landscape = {
            'active_proposals': len([p for p in tool_marketplace.proposals.values() 
                                   if p.status == 'proposed']),
            'completed_tools': len(tool_marketplace.completed_tools),
            'tool_categories': {},
            'dependency_chains': []
        }
        
        # Categorize tools by functionality
        for tool_name, tool_data in tool_marketplace.completed_tools.items():
            category = self._categorize_tool(tool_name, tool_data.get('description', ''))
            landscape['tool_categories'][category] = landscape['tool_categories'].get(category, 0) + 1
            
        return landscape
    
    def _categorize_tools(self, tool_landscape: Dict) -> Dict[str, int]:
        """Categorize tools to identify oversaturated areas."""
        return tool_landscape.get('tool_categories', {})
    
    def _categorize_tool(self, tool_name: str, description: str) -> str:
        """Categorize a tool based on its name and description."""
        name_lower = tool_name.lower()
        desc_lower = description.lower()
        
        if 'data' in name_lower or 'parser' in name_lower:
            return 'data_processing'
        elif 'code' in name_lower or 'interpreter' in name_lower:
            return 'code_tools'
        elif 'api' in name_lower or 'connector' in name_lower:
            return 'integration'
        elif 'logic' in name_lower or 'engine' in name_lower:
            return 'logic_systems'
        else:
            return 'general_utilities'
    
    def _identify_ecosystem_gaps(self, tool_landscape: Dict) -> List[str]:
        """Identify gaps in the tool ecosystem."""
        categories = tool_landscape.get('tool_categories', {})
        expected_categories = ['data_processing', 'code_tools', 'integration', 'logic_systems', 'general_utilities']
        
        gaps = []
        for category in expected_categories:
            if categories.get(category, 0) < 2:  # Less than 2 tools in category
                gaps.append(category)
                
        return gaps
    
    def _find_complementary_tools(self, tool_landscape: Dict) -> List[str]:
        """Find opportunities for complementary tool development."""
        # Simplified: look for tools that could work together
        categories = tool_landscape.get('tool_categories', {})
        
        complementary_pairs = [
            ('data_processing', 'logic_systems'),
            ('code_tools', 'integration'),
            ('general_utilities', 'data_processing')
        ]
        
        opportunities = []
        for cat1, cat2 in complementary_pairs:
            if categories.get(cat1, 0) > 0 and categories.get(cat2, 0) == 0:
                opportunities.append(cat2)
            elif categories.get(cat2, 0) > 0 and categories.get(cat1, 0) == 0:
                opportunities.append(cat1)
                
        return opportunities
    
    def _get_agent_reputation(self, agent_id: str, tool_marketplace: Any) -> Dict:
        """Get reputation data for all agents."""
        reputation_data = {}
        
        # Get all agents from marketplace
        all_agents = set()
        for proposal in tool_marketplace.proposals.values():
            all_agents.add(proposal.proposer)
            all_agents.update(proposal.supporters)
            all_agents.update(proposal.builders)
            
        for tool_data in tool_marketplace.completed_tools.values():
            all_agents.update(tool_data.get('builders', []))
            
        # Get reputation for each agent
        for agent in all_agents:
            reputation_data[agent] = tool_marketplace.get_agent_reputation(agent)
            
        return reputation_data
    
    def get_recommended_action(self, agent_id: str, agents: List[Any], 
                             tool_marketplace: Any, communication_board: Any) -> str:
        """
        Get the recommended action for an agent based on Cognitive Boids forces.
        
        Returns the action type with highest combined force.
        """
        forces = self.compute_cognitive_forces(agent_id, agents, tool_marketplace, communication_board)
        
        # Find action with highest force
        recommended_action = max(forces.items(), key=lambda x: x[1])
        
        return recommended_action[0]
    
    def update_metrics(self, agent_id: str, action_taken: str, result: Dict):
        """Update tracking metrics for research analysis."""
        
        # Track agent role evolution
        self.agent_roles[agent_id].append({
            'action': action_taken,
            'success': result.get('success', False),
            'energy_gain': result.get('energy_gain', 0),
            'timestamp': result.get('timestamp', 'unknown')
        })
        
        # Track collaboration network
        if 'support' in action_taken or 'message' in action_taken:
            # Extract target agent from result if available
            target = result.get('target_agent')
            if target:
                self.collaboration_network[agent_id].add(target)
                self.collaboration_network[target].add(agent_id)
    
    def analyze_emergence_patterns(self) -> Dict[str, Any]:
        """
        Analyze emergence patterns for research insights.
        
        Returns metrics about specialization, network effects, and tool evolution.
        """
        
        # Agent specialization analysis
        specialization_metrics = {}
        for agent_id, actions in self.agent_roles.items():
            action_types = [a['action'] for a in actions]
            action_diversity = len(set(action_types)) / max(len(action_types), 1)
            
            # Specialization index (lower = more specialized)
            specialization_metrics[agent_id] = {
                'diversity_index': action_diversity,
                'primary_role': max(set(action_types), key=action_types.count) if action_types else 'none',
                'total_actions': len(actions),
                'success_rate': sum(1 for a in actions if a['success']) / max(len(actions), 1)
            }
        
        # Network analysis
        network_metrics = {
            'total_connections': sum(len(connections) for connections in self.collaboration_network.values()) // 2,
            'most_connected_agent': max(self.collaboration_network.items(), 
                                      key=lambda x: len(x[1]), default=('none', set()))[0],
            'average_connections': np.mean([len(connections) for connections in self.collaboration_network.values()])
            if self.collaboration_network else 0
        }
        
        return {
            'specialization': specialization_metrics,
            'network': network_metrics,
            'total_agents_tracked': len(self.agent_roles)
        } 