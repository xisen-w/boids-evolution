"""
Simple Boids Agent - Ultra Minimal Implementation

CORE FOCUS: Tools + Neighbors + 3 Boids Rules
- No energy, no survival, no complexity
- Pure research focus on emergent collaboration

3 BOIDS RULES:
1. SEPARATION: Avoid building exact same tools as neighbors  
2. ALIGNMENT: Copy successful neighbors' strategies
3. COHESION: Build on/use neighbors' tools
"""

import random
from typing import List, Dict, Any


class SimpleBoid:
    """
    ULTRA MINIMAL: Just tools + neighbors + 3 boids rules.
    No energy, no survival, no complexity - pure research focus.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.tools = []  # Tools I've created: [{'type': 'data', 'id': 'tool_1', 'creator': 'Agent_01'}, ...]
        self.recent_actions = []  # Last few actions for pattern tracking
        self.neighbors = []  # Set by network topology
        
        # Boids rule weights (ready for genetics later)
        self.separation_weight = 0.4
        self.alignment_weight = 0.3
        self.cohesion_weight = 0.3
        
        # Available tool types for building
        self.tool_types = ['data', 'logic', 'utility', 'connector']
        
    def set_neighbors(self, neighbors: List['SimpleBoid']):
        """Set who I can observe in the network."""
        self.neighbors = neighbors
        
    def observe_neighbors(self) -> Dict[str, Any]:
        """What I can see about my neighbors (local observation only)."""
        return {
            'neighbor_tools': [n.tools for n in self.neighbors],
            'neighbor_recent_actions': [n.recent_actions[-3:] if n.recent_actions else [] for n in self.neighbors]
        }
    
    def apply_separation_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """
        SEPARATION: Avoid building the EXACT SAME TOOLS that neighbors just built.
        Creates niche finding and specialization.
        """
        # Start with equal preferences for all tool types
        action_prefs = {}
        for tool_type in self.tool_types:
            action_prefs[f'build_{tool_type}'] = 1.0
        action_prefs['use_tool'] = 0.3
        action_prefs['rest'] = 0.2
        
        # Find what EXACT TOOLS neighbors recently built
        recent_neighbor_tools = []
        for neighbor_tools in observations['neighbor_tools']:
            # Get their most recent tools (last 2-3 tools)
            recent_tools = neighbor_tools[-3:] if len(neighbor_tools) >= 3 else neighbor_tools
            recent_neighbor_tools.extend(recent_tools)
        
        # Also check what they built in recent actions
        for actions in observations['neighbor_recent_actions']:
            for action in actions:
                if action.startswith('build_'):
                    # Extract tool type from action
                    tool_type = action.split('_')[1]
                    # Add to recent tools (temporary tracking)
                    recent_neighbor_tools.append({'type': tool_type, 'recently_built': True})
        
        # Reduce preference for building tools that neighbors already have
        for recent_tool in recent_neighbor_tools:
            tool_type = recent_tool['type']
            
            # Count how many of this type neighbors have
            type_count = sum(1 for t in recent_neighbor_tools if t['type'] == tool_type)
            
            # Apply separation pressure based on saturation
            if type_count >= 2:  # If 2+ neighbors have this type
                action_prefs[f'build_{tool_type}'] *= 0.1  # Strongly avoid (niche finding)
            elif type_count == 1:
                action_prefs[f'build_{tool_type}'] *= 0.5  # Moderately avoid
        
        return action_prefs
    
    def apply_alignment_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """
        ALIGNMENT: Copy what successful neighbors do.
        Success = having more tools (productivity measure).
        """
        # Default equal preferences
        action_prefs = {}
        for tool_type in self.tool_types:
            action_prefs[f'build_{tool_type}'] = 0.25  # Equal split among tool types
        action_prefs['use_tool'] = 0.4
        action_prefs['rest'] = 0.2
        
        # Find neighbors with more tools (success = more tools created)
        successful_neighbors = [n for n in self.neighbors if len(n.tools) > len(self.tools)]
        
        if successful_neighbors:
            # Copy their recent actions (alignment behavior)
            successful_actions = []
            for neighbor in successful_neighbors:
                successful_actions.extend(neighbor.recent_actions[-2:])  # Last 2 actions
            
            # Boost preference for their common actions
            for action in successful_actions:
                if action in action_prefs:
                    action_prefs[action] = min(0.8, action_prefs[action] + 0.3)  # Boost but cap at 0.8
                
        return action_prefs
    
    def apply_cohesion_rule(self, observations: Dict[str, Any]) -> Dict[str, float]:
        """
        COHESION: Build on/use neighbors' tools.
        Stay connected to productive neighbors through tool usage.
        """
        action_prefs = {}
        for tool_type in self.tool_types:
            action_prefs[f'build_{tool_type}'] = 0.2
        action_prefs['use_tool'] = 0.5
        action_prefs['rest'] = 0.2
        
        # Count total neighbor tools available
        total_neighbor_tools = sum(len(tools) for tools in observations['neighbor_tools'])
        
        # If neighbors have tools, prefer using them (cohesion behavior)
        if total_neighbor_tools > 0:
            action_prefs['use_tool'] = 0.6  # Strong preference for using neighbor tools
            # Also slightly boost building complementary tools
            for tool_type in self.tool_types:
                action_prefs[f'build_{tool_type}'] = 0.25
            
        return action_prefs
    
    def choose_action(self, sep_prefs: Dict[str, float], align_prefs: Dict[str, float], cohes_prefs: Dict[str, float]) -> str:
        """
        Combine 3 boids rules to choose action using WEIGHTED RANDOM SELECTION.
        
        The weights (separation_weight, alignment_weight, cohesion_weight) determine
        how much each rule influences the final decision.
        """
        # Get all possible actions
        all_actions = set(sep_prefs.keys()) | set(align_prefs.keys()) | set(cohes_prefs.keys())
        
        # Calculate final weighted preferences (core boids combination)
        final_prefs = {}
        for action in all_actions:
            final_prefs[action] = (
                sep_prefs.get(action, 0) * self.separation_weight +
                align_prefs.get(action, 0) * self.alignment_weight +
                cohes_prefs.get(action, 0) * self.cohesion_weight
            )
        
        # Weighted random choice - higher preferences = higher probability
        actions = list(final_prefs.keys())
        weights = list(final_prefs.values())
        
        # Ensure we have valid weights
        if all(w <= 0 for w in weights):
            weights = [1.0] * len(weights)  # Fallback to equal weights
        
        return random.choices(actions, weights=weights)[0]
    
    def step(self) -> Dict[str, Any]:
        """
        ONE BOIDS STEP: Observe → Apply 3 Rules → Act
        
        This is the core boids loop that creates emergent behavior.
        """
        # 1. Observe neighbors (local information only)
        observations = self.observe_neighbors()
        
        # 2. Apply the 3 boids rules
        sep_prefs = self.apply_separation_rule(observations)
        align_prefs = self.apply_alignment_rule(observations)
        cohes_prefs = self.apply_cohesion_rule(observations)
        
        # 3. Choose action based on weighted combination
        action = self.choose_action(sep_prefs, align_prefs, cohes_prefs)
        
        # 4. Execute action
        if action.startswith('build_'):
            tool_type = action.split('_')[1]  # 'build_data' -> 'data'
            
            # Generate unique tool to avoid exact duplicates
            existing_tools_of_type = [t for t in self.tools if t['type'] == tool_type]
            tool_variant = len(existing_tools_of_type) + 1
            
            # Create unique tool
            tool_id = f"{tool_type}_tool_v{tool_variant}_{self.agent_id}"
            new_tool = {
                'type': tool_type, 
                'id': tool_id,
                'creator': self.agent_id,
                'variant': tool_variant
            }
            self.tools.append(new_tool)
            result_info = f"built {tool_id}"
            
        elif action == 'use_tool':
            # Use a random neighbor's tool (if any exist)
            all_neighbor_tools = []
            for n_tools in observations['neighbor_tools']:
                all_neighbor_tools.extend(n_tools)
            if all_neighbor_tools:
                used_tool = random.choice(all_neighbor_tools)
                result_info = f"used {used_tool['id']}"
            else:
                result_info = "tried to use tool (none available)"
                
        else:  # rest
            result_info = "rested"
        
        # 5. Track action for future boids decisions
        self.recent_actions.append(action)
        if len(self.recent_actions) > 5:
            self.recent_actions.pop(0)  # Keep only recent history
            
        return {
            'agent_id': self.agent_id,
            'action': action,
            'info': result_info,
            'tools_count': len(self.tools),
            'tools': [t['id'] for t in self.tools],  # Show actual tool names
            'rule_preferences': {
                'separation': sep_prefs,
                'alignment': align_prefs, 
                'cohesion': cohes_prefs
            }
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state for analysis."""
        tool_types = [t['type'] for t in self.tools]
        type_counts = {}
        for tool_type in tool_types:
            type_counts[tool_type] = type_counts.get(tool_type, 0) + 1
            
        return {
            'agent_id': self.agent_id,
            'tools_created': len(self.tools),
            'tool_type_distribution': type_counts,
            'recent_actions': self.recent_actions[-3:],
            'boids_weights': {
                'separation': self.separation_weight,
                'alignment': self.alignment_weight,
                'cohesion': self.cohesion_weight
            }
        } 