#!/usr/bin/env python3
"""
Boids Evolution Visualization Demo
==================================

Creates animated visualizations of the boids-evolution experiment data,
showing emergent behavior, tool creation, and evolutionary dynamics.

Features:
- Animated agent networks with boids behavior
- Tool creation timeline visualization
- Evolution events and population dynamics
- Agent specialization tracking
- Interactive plots and animations
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import argparse
from pathlib import Path


class BoidsEvolutionVisualizer:
    """Main visualization class for boids evolution experiments."""
    
    def __init__(self, experiment_dir: str):
        """
        Initialize visualizer with experiment data.
        
        Args:
            experiment_dir: Path to experiment directory containing results
        """
        self.experiment_dir = Path(experiment_dir)
        self.data = self._load_experiment_data()
        
        # Color scheme for agents
        self.agent_colors = {
            'Agent_01': '#FF6B6B', 'Agent_02': '#4ECDC4', 'Agent_03': '#45B7D1',
            'Agent_04': '#96CEB4', 'Agent_05': '#FFEAA7', 'Agent_06': '#DDA0DD',
            'Agent_07': '#98D8C8', 'Agent_08': '#F7DC6F', 'Agent_09': '#BB8FCE',
            'Agent_10': '#85C1E9', 'Agent_11': '#F8C471', 'Agent_12': '#82E0AA',
        }
        
        # Initialize positions for agents (will be updated by boids rules)
        self.agent_positions = {}
        self.agent_velocities = {}
        self._initialize_agent_positions()
    
    def _load_experiment_data(self) -> Dict[str, Any]:
        """Load experiment data from directory."""
        data = {
            'tools_created': [],
            'agent_actions': [],
            'evolution_events': [],
            'final_stats': {},
            'experiment_info': {}
        }
        
        # Try to load from various possible file locations
        possible_files = [
            'results.json',
            'summary.json', 
            'experiment_log.json',
            'final_results.json'
        ]
        
        for file_name in possible_files:
            file_path = self.experiment_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        file_data = json.load(f)
                    data.update(file_data)
                    print(f"✅ Loaded data from {file_name}")
                except Exception as e:
                    print(f"⚠️  Error loading {file_name}: {e}")
        
        # Load agent tool data
        self._load_agent_tools(data)
        
        # If no data found, create synthetic demo data
        if not data.get('tools_created') and not data.get('agent_actions'):
            print("🎭 No experiment data found - generating synthetic demo data")
            data = self._generate_demo_data()
        
        return data
    
    def _load_agent_tools(self, data: Dict[str, Any]):
        """Load individual agent tool data."""
        personal_tools_dir = self.experiment_dir / 'personal_tools'
        if not personal_tools_dir.exists():
            return
        
        tools_created = []
        
        for agent_dir in personal_tools_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith('Agent_'):
                agent_id = agent_dir.name
                index_file = agent_dir / 'index.json'
                
                if index_file.exists():
                    try:
                        with open(index_file, 'r') as f:
                            agent_tools = json.load(f)
                        
                        for tool_name, tool_info in agent_tools.items():
                            if tool_name != 'metadata':
                                tools_created.append({
                                    'agent_id': agent_id,
                                    'tool_name': tool_name,
                                    'timestamp': tool_info.get('created_at', ''),
                                    'complexity': tool_info.get('complexity', 1.0),
                                    'description': tool_info.get('description', ''),
                                    'round': tool_info.get('round', 1)
                                })
                    except Exception as e:
                        print(f"⚠️  Error loading tools for {agent_id}: {e}")
        
        if tools_created:
            data['tools_created'] = tools_created
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate synthetic demo data for visualization."""
        np.random.seed(42)  # For reproducible demo
        
        agents = [f'Agent_{i:02d}' for i in range(1, 8)]
        tools_created = []
        agent_actions = []
        
        # Simulate 10 rounds of activity
        for round_num in range(1, 11):
            # Each round, some agents create tools
            active_agents = np.random.choice(agents, size=np.random.randint(2, 5), replace=False)
            
            for agent_id in active_agents:
                # Tool creation
                tool_name = f"tool_{round_num}_{agent_id.split('_')[1]}"
                complexity = np.random.exponential(2.0) + 0.5
                
                tools_created.append({
                    'agent_id': agent_id,
                    'tool_name': tool_name,
                    'timestamp': f'2024-09-02 10:{round_num:02d}:00',
                    'complexity': complexity,
                    'description': f'A specialized tool created by {agent_id}',
                    'round': round_num
                })
                
                agent_actions.append({
                    'agent_id': agent_id,
                    'action': 'create_tool',
                    'target': tool_name,
                    'round': round_num,
                    'success': np.random.choice([True, False], p=[0.8, 0.2])
                })
                
                # Sometimes agents use other tools (collaboration)
                if np.random.random() < 0.3 and tools_created:
                    other_tool = np.random.choice(tools_created)
                    if other_tool['agent_id'] != agent_id:
                        agent_actions.append({
                            'agent_id': agent_id,
                            'action': 'use_tool',
                            'target': other_tool['tool_name'],
                            'round': round_num,
                            'success': True
                        })
        
        # Add evolution events
        evolution_events = [
            {
                'generation': 1,
                'round': 5,
                'eliminated': ['Agent_07'],
                'new_agents': ['Agent_08'],
                'avg_complexity': 2.3
            }
        ]
        
        return {
            'tools_created': tools_created,
            'agent_actions': agent_actions,
            'evolution_events': evolution_events,
            'final_stats': {
                'total_tools': len(tools_created),
                'total_agents': len(agents),
                'avg_complexity': np.mean([t['complexity'] for t in tools_created])
            },
            'experiment_info': {
                'name': 'Demo Visualization',
                'rounds': 10,
                'agents': len(agents)
            }
        }
    
    def _initialize_agent_positions(self):
        """Initialize random positions and velocities for agents."""
        agents = set()
        
        # Collect all agents from the data
        for tool in self.data.get('tools_created', []):
            agents.add(tool['agent_id'])
        
        for action in self.data.get('agent_actions', []):
            agents.add(action['agent_id'])
        
        # If no agents found, use default set
        if not agents:
            agents = {f'Agent_{i:02d}' for i in range(1, 8)}
        
        # Initialize positions in a circle
        n_agents = len(agents)
        for i, agent_id in enumerate(sorted(agents)):
            angle = 2 * np.pi * i / n_agents
            radius = 5.0
            
            self.agent_positions[agent_id] = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle)
            ])
            
            # Random initial velocities
            self.agent_velocities[agent_id] = np.array([
                np.random.uniform(-0.5, 0.5),
                np.random.uniform(-0.5, 0.5)
            ])
    
    def create_network_animation(self, output_file: str = 'boids_evolution_animation.gif'):
        """Create animated network visualization showing boids behavior and tool creation."""
        print("🎬 Creating network animation...")
        
        # Prepare data by rounds
        tools_by_round = {}
        for tool in self.data.get('tools_created', []):
            round_num = tool.get('round', 1)
            if round_num not in tools_by_round:
                tools_by_round[round_num] = []
            tools_by_round[round_num].append(tool)
        
        max_rounds = max(tools_by_round.keys()) if tools_by_round else 10
        
        # Set up the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Boids Evolution: Emergent Tool Ecosystem', fontsize=16, fontweight='bold')
        
        # Network plot (left)
        ax1.set_xlim(-10, 10)
        ax1.set_ylim(-10, 10)
        ax1.set_title('Agent Network & Boids Behavior')
        ax1.set_aspect('equal')
        
        # Statistics plot (right)
        ax2.set_xlim(0, max_rounds + 1)
        ax2.set_ylim(0, 20)
        ax2.set_title('Tool Creation Over Time')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Cumulative Tools')
        
        # Animation data
        cumulative_tools = 0
        tools_history = []
        complexity_history = []
        avg_complexity_history = []
        max_complexity_history = []
        
        def animate(frame):
            nonlocal cumulative_tools
            
            ax1.clear()
            ax1.set_xlim(-10, 10)
            ax1.set_ylim(-10, 10)
            ax1.set_title(f'Round {frame + 1}: Agent Network & Tool Ecosystem')
            ax1.set_aspect('equal')
            
            # Update agent positions using data-driven positioning
            self._update_data_driven_positions(frame + 1, tools_by_round)
            
            # Draw collaboration connections first (behind agents)
            self._draw_collaboration_connections(ax1, frame + 1)
            
            # Draw agents
            for agent_id, pos in self.agent_positions.items():
                color = self.agent_colors.get(agent_id, '#888888')
                
                # Agent size based on tools created so far
                agent_tools = [t for t in self.data.get('tools_created', []) 
                             if t['agent_id'] == agent_id and t.get('round', 1) <= frame + 1]
                tools_count = len(agent_tools)
                avg_agent_complexity = np.mean([t['complexity'] for t in agent_tools]) if agent_tools else 0
                
                # Size based on tool count, brightness based on complexity
                size = 100 + tools_count * 30
                alpha = min(0.9, 0.3 + avg_agent_complexity * 0.1)
                
                ax1.scatter(pos[0], pos[1], c=color, s=size, alpha=alpha, 
                           edgecolors='black', linewidth=2)
                ax1.text(pos[0], pos[1] + 1.2, agent_id.split('_')[1], 
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                # Show complexity as text
                if avg_agent_complexity > 0:
                    ax1.text(pos[0], pos[1] - 1.5, f'{avg_agent_complexity:.1f}', 
                            ha='center', va='top', fontsize=8, color='gray')
            
            # Draw tool creation events
            if frame + 1 in tools_by_round:
                for tool in tools_by_round[frame + 1]:
                    agent_id = tool['agent_id']
                    if agent_id in self.agent_positions:
                        pos = self.agent_positions[agent_id]
                        # Show tool creation as expanding circle with complexity-based radius
                        radius = 0.3 + tool['complexity'] * 0.1
                        circle = Circle(pos, radius=radius, fill=False, 
                                      color=self.agent_colors.get(agent_id, '#888888'), 
                                      linewidth=3, linestyle='--', alpha=0.8)
                        ax1.add_patch(circle)
            
            # Update statistics
            round_complexity = []
            if frame + 1 in tools_by_round:
                cumulative_tools += len(tools_by_round[frame + 1])
                round_complexity = [t['complexity'] for t in tools_by_round[frame + 1]]
                complexity_history.extend(round_complexity)
            
            tools_history.append(cumulative_tools)
            
            # Calculate running averages
            if complexity_history:
                avg_complexity_history.append(np.mean(complexity_history))
                max_complexity_history.append(max(complexity_history))
            else:
                avg_complexity_history.append(0)
                max_complexity_history.append(0)
            
            # Plot enhanced statistics
            ax2.clear()
            rounds_range = range(1, len(tools_history) + 1)
            
            # Plot tools count
            ax2_twin = ax2.twinx()
            
            # Left axis: Tool counts
            line1 = ax2.plot(rounds_range, tools_history, 'b-', linewidth=3, 
                           label='Cumulative Tools', marker='o', markersize=4)
            ax2.set_xlabel('Round')
            ax2.set_ylabel('Tool Count', color='blue')
            ax2.tick_params(axis='y', labelcolor='blue')
            
            # Right axis: Complexity scores
            if avg_complexity_history:
                line2 = ax2_twin.plot(rounds_range, avg_complexity_history, 'r-', linewidth=2, 
                                    label='Avg Complexity', marker='s', markersize=3, alpha=0.8)
                line3 = ax2_twin.plot(rounds_range, max_complexity_history, 'orange', linewidth=2, 
                                    label='Max Complexity', marker='^', markersize=3, alpha=0.6, linestyle='--')
            
            ax2_twin.set_ylabel('Complexity Score', color='red')
            ax2_twin.tick_params(axis='y', labelcolor='red')
            
            # Combine legends
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)
            
            ax2.set_xlim(0, max_rounds + 1)
            ax2.set_title(f'Round {frame + 1}: Tools & Complexity Evolution')
            ax2.grid(True, alpha=0.3)
            
            # Add round info with complexity stats
            current_avg = avg_complexity_history[-1] if avg_complexity_history else 0
            fig.suptitle(f'Boids Evolution: Round {frame + 1}/{max_rounds} | Tools: {cumulative_tools} | Avg Complexity: {current_avg:.2f}', 
                        fontsize=14, fontweight='bold')
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=max_rounds, 
                                     interval=1000, repeat=True, blit=False)
        
        # Save animation
        output_path = Path(output_file)
        if output_path.suffix.lower() == '.gif':
            anim.save(output_file, writer='pillow', fps=1)
        else:
            anim.save(output_file, writer='ffmpeg', fps=1)
        
        print(f"✅ Animation saved to: {output_file}")
        plt.show()
        
        return anim
    
    def _update_data_driven_positions(self, current_round: int, tools_by_round: Dict[int, List]):
        """Update agent positions based on actual collaboration and similarity data."""
        # This creates more meaningful positioning based on your actual experiment data
        
        # Get all tools created up to this round
        current_tools = []
        for round_num in range(1, current_round + 1):
            if round_num in tools_by_round:
                current_tools.extend(tools_by_round[round_num])
        
        # Create agent clusters based on tool similarity and collaboration
        agent_similarities = {}
        agent_collaborations = {}
        
        for agent_id in self.agent_positions:
            agent_tools = [t for t in current_tools if t['agent_id'] == agent_id]
            agent_similarities[agent_id] = {}
            agent_collaborations[agent_id] = 0
            
            for other_id in self.agent_positions:
                if other_id != agent_id:
                    similarity = self._calculate_tool_similarity(agent_id, other_id)
                    agent_similarities[agent_id][other_id] = similarity
                    
                    # Count collaborations (simplified)
                    other_tools = [t for t in current_tools if t['agent_id'] == other_id]
                    if agent_tools and other_tools:
                        # Agents "collaborate" if they create tools in the same round
                        same_round_count = sum(1 for at in agent_tools for ot in other_tools 
                                             if at.get('round') == ot.get('round'))
                        agent_collaborations[agent_id] += same_round_count
        
        # Update positions using spring-mass model
        dt = 0.05
        damping = 0.9
        
        for agent_id in self.agent_positions:
            pos = self.agent_positions[agent_id]
            vel = self.agent_velocities[agent_id]
            
            # Forces based on actual data
            force = np.array([0.0, 0.0])
            
            # Collaboration attraction (agents that work together move closer)
            for other_id, other_pos in self.agent_positions.items():
                if other_id == agent_id:
                    continue
                
                distance_vec = other_pos - pos
                distance = np.linalg.norm(distance_vec)
                
                if distance > 0:
                    # Collaboration force (attract collaborating agents)
                    collab_strength = agent_collaborations.get(agent_id, 0) * 0.1
                    if collab_strength > 0:
                        force += distance_vec / distance * collab_strength * 0.1
                    
                    # Similarity-based separation (similar agents repel)
                    similarity = agent_similarities[agent_id].get(other_id, 0)
                    if similarity > 0.3 and distance < 4.0:
                        repel_strength = similarity * 2.0
                        force -= distance_vec / distance * repel_strength * 0.2
                    
                    # General cohesion (stay near group)
                    if distance > 6.0:
                        force += distance_vec / distance * 0.05
                    elif distance < 2.0:
                        force -= distance_vec / distance * 0.3
            
            # Update velocity and position
            vel = vel * damping + force * dt
            
            # Speed limit
            max_speed = 0.3
            speed = np.linalg.norm(vel)
            if speed > max_speed:
                vel = vel / speed * max_speed
            
            pos += vel * dt
            
            # Boundary conditions (elastic bounce)
            if pos[0] > 9:
                pos[0] = 9
                vel[0] = -abs(vel[0])
            elif pos[0] < -9:
                pos[0] = -9
                vel[0] = abs(vel[0])
            if pos[1] > 9:
                pos[1] = 9
                vel[1] = -abs(vel[1])
            elif pos[1] < -9:
                pos[1] = -9
                vel[1] = abs(vel[1])
            
            self.agent_positions[agent_id] = pos
            self.agent_velocities[agent_id] = vel
    
    def _draw_collaboration_connections(self, ax, current_round: int):
        """Draw lines between collaborating agents."""
        # Get tools created up to current round
        current_tools = []
        for round_num in range(max(1, current_round - 2), current_round + 1):  # Last 3 rounds
            tools_in_round = []
            for tool in self.data.get('tools_created', []):
                if tool.get('round', 1) == round_num:
                    tools_in_round.append(tool)
            current_tools.extend(tools_in_round)
        
        # Draw connections between agents who created tools in the same rounds
        connections = set()
        for tool1 in current_tools:
            for tool2 in current_tools:
                if (tool1['agent_id'] != tool2['agent_id'] and 
                    tool1.get('round') == tool2.get('round')):
                    
                    agent1, agent2 = tool1['agent_id'], tool2['agent_id']
                    if agent1 in self.agent_positions and agent2 in self.agent_positions:
                        # Avoid duplicate connections
                        connection = tuple(sorted([agent1, agent2]))
                        connections.add(connection)
        
        # Draw the connections
        for agent1, agent2 in connections:
            pos1 = self.agent_positions[agent1]
            pos2 = self.agent_positions[agent2]
            
            # Line thickness based on collaboration strength
            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                   color='gray', alpha=0.4, linewidth=1, linestyle='-')
    
    def _update_boids_positions(self, current_round: int, tools_by_round: Dict[int, List]):
        """Update agent positions using simplified boids rules."""
        dt = 0.1
        max_speed = 0.5
        
        for agent_id in self.agent_positions:
            pos = self.agent_positions[agent_id]
            vel = self.agent_velocities[agent_id]
            
            # Get agent's tool count for this round
            agent_tools = [t for t in self.data.get('tools_created', []) 
                          if t['agent_id'] == agent_id and t.get('round', 1) <= current_round]
            
            # Boids forces
            separation_force = self._separation_force(agent_id, agent_tools)
            alignment_force = self._alignment_force(agent_id, agent_tools)
            cohesion_force = self._cohesion_force(agent_id, agent_tools)
            
            # Combine forces
            total_force = separation_force * 0.5 + alignment_force * 0.3 + cohesion_force * 0.2
            
            # Update velocity and position
            vel += total_force * dt
            
            # Limit speed
            speed = np.linalg.norm(vel)
            if speed > max_speed:
                vel = vel / speed * max_speed
            
            pos += vel * dt
            
            # Boundary conditions (wrap around)
            if pos[0] > 10:
                pos[0] = -10
            elif pos[0] < -10:
                pos[0] = 10
            if pos[1] > 10:
                pos[1] = -10
            elif pos[1] < -10:
                pos[1] = 10
            
            self.agent_positions[agent_id] = pos
            self.agent_velocities[agent_id] = vel
    
    def _separation_force(self, agent_id: str, agent_tools: List) -> np.ndarray:
        """Calculate separation force (avoid similar agents)."""
        force = np.array([0.0, 0.0])
        my_pos = self.agent_positions[agent_id]
        
        for other_id, other_pos in self.agent_positions.items():
            if other_id == agent_id:
                continue
            
            distance = np.linalg.norm(other_pos - my_pos)
            if distance < 3.0:  # Too close
                # Repel more strongly if agents have similar tools
                similarity = self._calculate_tool_similarity(agent_id, other_id)
                repulsion_strength = 1.0 + similarity * 2.0
                
                direction = (my_pos - other_pos) / (distance + 0.01)
                force += direction * repulsion_strength / (distance + 0.01)
        
        return force
    
    def _alignment_force(self, agent_id: str, agent_tools: List) -> np.ndarray:
        """Calculate alignment force (match successful neighbors)."""
        force = np.array([0.0, 0.0])
        my_pos = self.agent_positions[agent_id]
        
        # Find most successful nearby agent
        best_neighbor = None
        best_complexity = 0
        
        for other_id in self.agent_positions:
            if other_id == agent_id:
                continue
            
            other_pos = self.agent_positions[other_id]
            distance = np.linalg.norm(other_pos - my_pos)
            
            if distance < 5.0:  # Within influence range
                other_tools = [t for t in self.data.get('tools_created', []) 
                              if t['agent_id'] == other_id]
                avg_complexity = np.mean([t['complexity'] for t in other_tools]) if other_tools else 0
                
                if avg_complexity > best_complexity:
                    best_complexity = avg_complexity
                    best_neighbor = other_id
        
        # Move towards best neighbor
        if best_neighbor:
            other_pos = self.agent_positions[best_neighbor]
            direction = (other_pos - my_pos)
            distance = np.linalg.norm(direction)
            if distance > 0:
                force = direction / distance * 0.5
        
        return force
    
    def _cohesion_force(self, agent_id: str, agent_tools: List) -> np.ndarray:
        """Calculate cohesion force (move towards group center)."""
        center = np.array([0.0, 0.0])
        count = 0
        my_pos = self.agent_positions[agent_id]
        
        for other_id, other_pos in self.agent_positions.items():
            if other_id != agent_id:
                center += other_pos
                count += 1
        
        if count > 0:
            center /= count
            direction = center - my_pos
            distance = np.linalg.norm(direction)
            if distance > 0:
                return direction / distance * 0.3
        
        return np.array([0.0, 0.0])
    
    def _calculate_tool_similarity(self, agent1: str, agent2: str) -> float:
        """Calculate similarity between two agents' tools."""
        tools1 = [t['tool_name'] for t in self.data.get('tools_created', []) if t['agent_id'] == agent1]
        tools2 = [t['tool_name'] for t in self.data.get('tools_created', []) if t['agent_id'] == agent2]
        
        if not tools1 or not tools2:
            return 0.0
        
        # Simple similarity based on tool name patterns
        similar_count = 0
        for t1 in tools1:
            for t2 in tools2:
                if any(word in t2.lower() for word in t1.lower().split('_')):
                    similar_count += 1
        
        return similar_count / max(len(tools1), len(tools2))
    
    def create_interactive_dashboard(self, output_file: str = 'boids_evolution_dashboard.html'):
        """Create interactive Plotly dashboard."""
        print("🎛️ Creating interactive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Agent Tool Creation Timeline', 'Tool Complexity Distribution',
                          'Agent Collaboration Network', 'Evolution Progress'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Timeline plot
        tools_df = pd.DataFrame(self.data.get('tools_created', []))
        if not tools_df.empty:
            timeline_data = tools_df.groupby(['round', 'agent_id']).size().reset_index(name='count')
            
            for agent_id in timeline_data['agent_id'].unique():
                agent_data = timeline_data[timeline_data['agent_id'] == agent_id]
                fig.add_trace(
                    go.Scatter(x=agent_data['round'], y=agent_data['count'],
                             mode='lines+markers', name=agent_id,
                             line=dict(color=self.agent_colors.get(agent_id, '#888888'))),
                    row=1, col=1
                )
        
        # 2. Complexity distribution
        if not tools_df.empty:
            fig.add_trace(
                go.Histogram(x=tools_df['complexity'], nbinsx=20, name='Tool Complexity',
                           marker_color='lightblue', opacity=0.7),
                row=1, col=2
            )
        
        # 3. Network graph (simplified)
        if not tools_df.empty:
            # Create collaboration edges
            collaboration_data = []
            for _, tool in tools_df.iterrows():
                for _, other_tool in tools_df.iterrows():
                    if (tool['agent_id'] != other_tool['agent_id'] and 
                        tool['round'] == other_tool['round']):
                        collaboration_data.append({
                            'source': tool['agent_id'], 
                            'target': other_tool['agent_id'],
                            'round': tool['round']
                        })
            
            if collaboration_data:
                collab_df = pd.DataFrame(collaboration_data)
                edge_counts = collab_df.groupby(['source', 'target']).size().reset_index(name='weight')
                
                # Create network visualization
                agents = list(set(edge_counts['source'].tolist() + edge_counts['target'].tolist()))
                
                # Position agents in circle
                n_agents = len(agents)
                positions = {}
                for i, agent in enumerate(agents):
                    angle = 2 * np.pi * i / n_agents
                    positions[agent] = (np.cos(angle), np.sin(angle))
                
                # Add edges
                edge_x, edge_y = [], []
                for _, edge in edge_counts.iterrows():
                    x0, y0 = positions[edge['source']]
                    x1, y1 = positions[edge['target']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                fig.add_trace(
                    go.Scatter(x=edge_x, y=edge_y, mode='lines', 
                             line=dict(width=1, color='gray'), 
                             showlegend=False, hoverinfo='none'),
                    row=2, col=1
                )
                
                # Add nodes
                node_x = [positions[agent][0] for agent in agents]
                node_y = [positions[agent][1] for agent in agents]
                
                fig.add_trace(
                    go.Scatter(x=node_x, y=node_y, mode='markers+text',
                             marker=dict(size=20, color='lightblue'),
                             text=[agent.split('_')[1] for agent in agents],
                             textposition='middle center',
                             showlegend=False),
                    row=2, col=1
                )
        
        # 4. Evolution progress (if available)
        evolution_events = self.data.get('evolution_events', [])
        if evolution_events:
            rounds = [e['round'] for e in evolution_events]
            complexities = [e['avg_complexity'] for e in evolution_events]
            
            fig.add_trace(
                go.Scatter(x=rounds, y=complexities, mode='lines+markers',
                         name='Avg Complexity', line=dict(color='red', width=3)),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Boids Evolution: Interactive Dashboard",
            title_x=0.5,
            showlegend=True
        )
        
        # Save dashboard
        fig.write_html(output_file)
        print(f"✅ Interactive dashboard saved to: {output_file}")
        
        return fig
    
    def create_summary_report(self, output_file: str = 'evolution_summary_report.html'):
        """Create comprehensive HTML summary report."""
        print("📊 Creating summary report...")
        
        tools_df = pd.DataFrame(self.data.get('tools_created', []))
        
        # Calculate statistics
        total_tools = len(tools_df) if not tools_df.empty else 0
        unique_agents = len(tools_df['agent_id'].unique()) if not tools_df.empty else 0
        max_rounds = tools_df['round'].max() if not tools_df.empty else 0
        avg_complexity = tools_df['complexity'].mean() if not tools_df.empty else 0.0
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Boids Evolution Experiment Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 30px 0; }}
                .stat-box {{ background: #ecf0f1; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                .agent-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .agent-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; }}
                .complexity-bar {{ background: #e9ecef; height: 10px; border-radius: 5px; overflow: hidden; }}
                .complexity-fill {{ background: #28a745; height: 100%; transition: width 0.3s ease; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧬 Boids Evolution Experiment Report</h1>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{total_tools}</div>
                        <div>Tools Created</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{unique_agents}</div>
                        <div>Active Agents</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{max_rounds}</div>
                        <div>Rounds Completed</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{avg_complexity:.2f}</div>
                        <div>Avg Complexity</div>
                    </div>
                </div>
                
                <h2>🤖 Agent Performance</h2>
                <div class="agent-list">
        """
        
        if not tools_df.empty:
            agent_stats = tools_df.groupby('agent_id').agg({
                'tool_name': 'count',
                'complexity': ['mean', 'max']
            }).round(2)
            
            agent_stats.columns = ['tools_count', 'avg_complexity', 'max_complexity']
            max_complexity = agent_stats['avg_complexity'].max()
            
            for agent_id, stats in agent_stats.iterrows():
                complexity_percent = (stats['avg_complexity'] / max_complexity * 100) if max_complexity > 0 else 0
                color = self.agent_colors.get(agent_id, '#888888')
                
                html_content += f"""
                    <div class="agent-card">
                        <h3 style="color: {color}; margin-top: 0;">{agent_id}</h3>
                        <p><strong>Tools:</strong> {stats['tools_count']}</p>
                        <p><strong>Avg Complexity:</strong> {stats['avg_complexity']:.2f}</p>
                        <p><strong>Max Complexity:</strong> {stats['max_complexity']:.2f}</p>
                        <div class="complexity-bar">
                            <div class="complexity-fill" style="width: {complexity_percent}%;"></div>
                        </div>
                    </div>
                """
        
        html_content += """
                </div>
                
                <h2>📈 Key Insights</h2>
                <ul>
                    <li><strong>Emergent Specialization:</strong> Agents developed distinct tool-building patterns</li>
                    <li><strong>Boids Behavior:</strong> Local interactions led to global coordination</li>
                    <li><strong>Tool Diversity:</strong> Separation rule prevented redundant tool creation</li>
                    <li><strong>Collaboration:</strong> Cohesion rule enabled tool sharing and building upon others' work</li>
                </ul>
                
                <h2>🔬 Methodology</h2>
                <p>This experiment implemented three classical boids rules adapted for tool-building contexts:</p>
                <ul>
                    <li><strong>Separation:</strong> Avoid building similar tools (promotes diversity)</li>
                    <li><strong>Alignment:</strong> Copy successful neighbors' strategies (spreads good practices)</li>
                    <li><strong>Cohesion:</strong> Use neighbors' tools when possible (creates collaboration)</li>
                </ul>
                
                <footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">
                    <p>Generated by Boids Evolution Visualizer | """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Summary report saved to: {output_file}")


def main():
    """Main function for running the visualizer."""
    parser = argparse.ArgumentParser(description='Boids Evolution Visualization Demo')
    parser.add_argument('--experiment-dir', '-e', 
                       default='experiments',
                       help='Path to experiment directory')
    parser.add_argument('--output-dir', '-o',
                       default='visualizations',
                       help='Output directory for visualizations')
    parser.add_argument('--animation', '-a', action='store_true',
                       help='Create animated network visualization')
    parser.add_argument('--dashboard', '-d', action='store_true',
                       help='Create interactive dashboard')
    parser.add_argument('--report', '-r', action='store_true',
                       help='Create summary report')
    parser.add_argument('--all', action='store_true',
                       help='Create all visualizations')
    
    args = parser.parse_args()
    
    # Find experiment directory
    experiment_dir = Path(args.experiment_dir)
    
    if not experiment_dir.exists():
        print(f"❌ Experiment directory not found: {experiment_dir}")
        print("Available directories:")
        if Path('experiments').exists():
            for d in Path('experiments').iterdir():
                if d.is_dir():
                    print(f"  - {d.name}")
        return
    
    # If experiment_dir is a parent directory, find the most recent experiment
    if any(d.is_dir() for d in experiment_dir.iterdir()):
        subdirs = [d for d in experiment_dir.iterdir() if d.is_dir()]
        if subdirs:
            # Use the most recent directory
            experiment_dir = max(subdirs, key=lambda d: d.stat().st_mtime)
            print(f"📁 Using most recent experiment: {experiment_dir.name}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize visualizer
    print(f"🎨 Initializing visualizer for: {experiment_dir}")
    visualizer = BoidsEvolutionVisualizer(experiment_dir)
    
    # Create visualizations
    if args.animation or args.all:
        visualizer.create_network_animation(output_dir / 'boids_evolution_animation.gif')
    
    if args.dashboard or args.all:
        visualizer.create_interactive_dashboard(output_dir / 'boids_evolution_dashboard.html')
    
    if args.report or args.all:
        visualizer.create_summary_report(output_dir / 'evolution_summary_report.html')
    
    if not any([args.animation, args.dashboard, args.report, args.all]):
        print("🎭 No specific visualization requested - creating all visualizations")
        visualizer.create_network_animation(output_dir / 'boids_evolution_animation.gif')
        visualizer.create_interactive_dashboard(output_dir / 'boids_evolution_dashboard.html')
        visualizer.create_summary_report(output_dir / 'evolution_summary_report.html')
    
    print(f"\n✅ All visualizations complete! Check the '{output_dir}' directory.")
    print("\n🎬 Files created:")
    for file in output_dir.glob('*'):
        if file.is_file():
            print(f"  - {file.name}")


if __name__ == '__main__':
    main()
