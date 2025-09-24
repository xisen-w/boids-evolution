"""
Tool Marketplace - Where agents propose, discuss, and build tools collaboratively.

This transforms the system from "using tools" to "building tools" based on 
inter-agent communication and collaborative development.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os


class ToolProposal:
    """A proposal for a new tool to be built."""
    
    def __init__(self, proposer: str, name: str, description: str, 
                 dependencies: List[str] = None, complexity: int = 1):
        self.proposer = proposer
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.complexity = complexity
        self.timestamp = datetime.now().isoformat()
        self.supporters = []
        self.comments = []
        self.status = "proposed"  # proposed, in_development, completed, rejected
        self.builders = []  # agents working on this
        self.energy_estimate = complexity * 10  # base energy for building
        
    def add_support(self, agent_id: str, comment: str = "") -> bool:
        """Add support from an agent."""
        if agent_id not in self.supporters:
            self.supporters.append(agent_id)
            if comment:
                self.add_comment(agent_id, f"Supporting: {comment}")
            return True
        return False
    
    def add_comment(self, agent_id: str, comment: str):
        """Add a comment to the proposal."""
        self.comments.append({
            'agent': agent_id,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        })
    
    def start_development(self, builder_agents: List[str]):
        """Start development with specified builders."""
        self.status = "in_development"
        self.builders = builder_agents.copy()
    
    def complete_development(self):
        """Mark the tool as completed."""
        self.status = "completed"
    
    def get_support_score(self) -> float:
        """Calculate support score based on supporters and comments."""
        return len(self.supporters) + (len(self.comments) * 0.5)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'proposer': self.proposer,
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
            'complexity': self.complexity,
            'timestamp': self.timestamp,
            'supporters': self.supporters,
            'comments': self.comments,
            'status': self.status,
            'builders': self.builders,
            'energy_estimate': self.energy_estimate,
            'support_score': self.get_support_score()
        }


class ToolMarketplace:
    """
    Marketplace where agents propose, discuss, and collaboratively build tools.
    
    Agents earn energy by:
    1. Proposing popular tool ideas
    2. Building tools that others use to create more tools
    3. Contributing to collaborative development
    """
    
    def __init__(self):
        self.proposals: Dict[str, ToolProposal] = {}  # proposal_id -> ToolProposal
        self.active_discussions: List[str] = []  # currently hot proposals
        self.completed_tools: Dict[str, Dict[str, Any]] = {}  # built tools
        self.agent_contributions: Dict[str, Dict[str, int]] = {}  # agent stats
        
    def propose_tool(self, agent_id: str, name: str, description: str, 
                    dependencies: List[str] = None, complexity: int = 1) -> str:
        """Propose a new tool for development."""
        proposal_id = f"{name}_{agent_id}_{len(self.proposals)}"
        
        proposal = ToolProposal(
            proposer=agent_id,
            name=name,
            description=description,
            dependencies=dependencies,
            complexity=complexity
        )
        
        self.proposals[proposal_id] = proposal
        self.active_discussions.append(proposal_id)
        
        # Track agent activity
        if agent_id not in self.agent_contributions:
            self.agent_contributions[agent_id] = {'proposals': 0, 'builds': 0, 'supports': 0}
        self.agent_contributions[agent_id]['proposals'] += 1
        
        return proposal_id
    
    def support_proposal(self, agent_id: str, proposal_id: str, comment: str = "") -> bool:
        """Support a tool proposal."""
        if proposal_id in self.proposals:
            success = self.proposals[proposal_id].add_support(agent_id, comment)
            if success:
                if agent_id not in self.agent_contributions:
                    self.agent_contributions[agent_id] = {'proposals': 0, 'builds': 0, 'supports': 0}
                self.agent_contributions[agent_id]['supports'] += 1
            return success
        return False
    
    def comment_on_proposal(self, agent_id: str, proposal_id: str, comment: str) -> bool:
        """Add a comment to a proposal."""
        if proposal_id in self.proposals:
            self.proposals[proposal_id].add_comment(agent_id, comment)
            return True
        return False
    
    def start_building(self, proposal_id: str, builder_agents: List[str]) -> bool:
        """Start building a tool from a proposal."""
        if proposal_id in self.proposals:
            proposal = self.proposals[proposal_id]
            proposal.start_development(builder_agents)
            
            # Track builder contributions
            for agent_id in builder_agents:
                if agent_id not in self.agent_contributions:
                    self.agent_contributions[agent_id] = {'proposals': 0, 'builds': 0, 'supports': 0}
                self.agent_contributions[agent_id]['builds'] += 1
            
            return True
        return False
    
    def complete_tool(self, proposal_id: str, tool_code: str) -> bool:
        """Complete a tool and add it to the registry."""
        if proposal_id in self.proposals:
            proposal = self.proposals[proposal_id]
            proposal.complete_development()
            
            # Add to completed tools
            self.completed_tools[proposal.name] = {
                'code': tool_code,
                'builders': proposal.builders,
                'proposer': proposal.proposer,
                'dependencies': proposal.dependencies,
                'completion_date': datetime.now().isoformat(),
                'proposal_id': proposal_id
            }
            
            # Remove from active discussions
            if proposal_id in self.active_discussions:
                self.active_discussions.remove(proposal_id)
            
            return True
        return False
    
    def get_popular_proposals(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular proposals by support score."""
        active_proposals = [
            (proposal_id, self.proposals[proposal_id]) 
            for proposal_id in self.active_discussions
            if self.proposals[proposal_id].status == "proposed"
        ]
        
        # Sort by support score
        sorted_proposals = sorted(
            active_proposals, 
            key=lambda x: x[1].get_support_score(), 
            reverse=True
        )
        
        return [
            {
                'proposal_id': prop_id,
                **proposal.to_dict()
            }
            for prop_id, proposal in sorted_proposals[:limit]
        ]
    
    def get_proposal_discussion(self, proposal_id: str) -> Dict[str, Any]:
        """Get full discussion for a proposal."""
        if proposal_id in self.proposals:
            proposal = self.proposals[proposal_id]
            return {
                'proposal': proposal.to_dict(),
                'discussion': proposal.comments,
                'supporters': proposal.supporters,
                'next_steps': self._suggest_next_steps(proposal)
            }
        return {}
    
    def _suggest_next_steps(self, proposal: ToolProposal) -> List[str]:
        """Suggest next steps for a proposal."""
        suggestions = []
        
        if proposal.status == "proposed":
            if len(proposal.supporters) >= 2:
                suggestions.append("Ready for development - find builders")
            else:
                suggestions.append("Needs more support - share with other agents")
                
        elif proposal.status == "in_development":
            suggestions.append("In development - check progress with builders")
            
        return suggestions
    
    def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """Get agent's reputation in the marketplace."""
        if agent_id not in self.agent_contributions:
            return {'proposals': 0, 'builds': 0, 'supports': 0, 'reputation_score': 0}
        
        stats = self.agent_contributions[agent_id]
        
        # Calculate reputation score
        reputation_score = (
            stats['proposals'] * 3 +  # Proposing tools
            stats['builds'] * 5 +     # Building tools  
            stats['supports'] * 1     # Supporting others
        )
        
        return {
            **stats,
            'reputation_score': reputation_score,
            'completed_tools': len([
                tool for tool in self.completed_tools.values()
                if agent_id in tool['builders'] or agent_id == tool['proposer']
            ])
        }
    
    def get_marketplace_summary(self) -> str:
        """Get formatted marketplace summary."""
        active_count = len([p for p in self.proposals.values() if p.status == "proposed"])
        building_count = len([p for p in self.proposals.values() if p.status == "in_development"])
        completed_count = len(self.completed_tools)
        
        summary = f"🛠️  Tool Marketplace Summary:\n"
        summary += f"  📋 Active proposals: {active_count}\n"
        summary += f"  🔨 In development: {building_count}\n"
        summary += f"  ✅ Completed tools: {completed_count}\n"
        
        if self.active_discussions:
            summary += f"\n🔥 Hot discussions:\n"
            popular = self.get_popular_proposals(3)
            for prop in popular:
                summary += f"  • {prop['name']}: {prop['support_score']:.1f} support\n"
        
        return summary
    
    def get_tool_building_context_for_agent(self, agent_id: str) -> str:
        """Get context for agent about current tool building opportunities."""
        context = "🛠️  Tool Building Opportunities:\n\n"
        
        # Proposals ready to build (have support)
        ready_to_build = [
            (pid, prop) for pid, prop in self.proposals.items()
            if prop.status == "proposed" and len(prop.supporters) >= 1 and prop.proposer != agent_id
        ]
        if ready_to_build:
            context += "🔨 Ready to BUILD (have support):\n"
            for pid, prop in ready_to_build:
                context += f"  • {prop.name}: {len(prop.supporters)} supporters - READY FOR BUILDING!\n"
        
        # Proposals needing support from others
        others_proposals = [
            (pid, prop) for pid, prop in self.proposals.items()
            if prop.status == "proposed" and prop.proposer != agent_id and len(prop.supporters) == 0
        ]
        if others_proposals:
            context += "👍 Others' proposals needing support:\n"
            for pid, prop in others_proposals[:3]:  # Show top 3
                context += f"  • {prop.name}: {prop.description[:50]}... (by {prop.proposer})\n"
        
        # Agent's own proposals
        my_proposals = [
            p for p in self.proposals.values() 
            if p.proposer == agent_id and p.status in ["proposed", "in_development"]
        ]
        if my_proposals:
            context += f"\n📋 Your active proposals:\n"
            for prop in my_proposals:
                context += f"  • {prop.name}: {prop.status} ({len(prop.supporters)} supporters)\n"
        
        # Reputation
        reputation = self.get_agent_reputation(agent_id)
        context += f"\n⭐ Your reputation: {reputation['reputation_score']} points\n"
        
        return context 