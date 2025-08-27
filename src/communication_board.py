"""
Communication Board - Enables real inter-agent communication.

Agents can post messages, read messages from others, and respond.
This creates genuine social dynamics and network effects.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class Message:
    """A message between agents."""
    
    def __init__(self, sender: str, content: str, recipient: str = None, message_type: str = "general"):
        self.sender = sender
        self.recipient = recipient  # None for broadcast
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now().isoformat()
        self.responses = []
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'content': self.content,
            'type': self.message_type,
            'timestamp': self.timestamp,
            'responses': self.responses
        }


class CommunicationBoard:
    """
    Shared communication board where agents can post and read messages.
    Enables real inter-agent communication and network effects.
    """
    
    def __init__(self):
        self.messages: List[Message] = []
        self.agent_connections: Dict[str, List[str]] = {}  # who talks to whom
        self.message_count: Dict[str, int] = {}  # messages per agent
        
    def post_message(self, sender: str, content: str, recipient: str = None, message_type: str = "general") -> bool:
        """Post a message to the board."""
        try:
            message = Message(sender, content, recipient, message_type)
            self.messages.append(message)
            
            # Track connections
            if sender not in self.agent_connections:
                self.agent_connections[sender] = []
            
            if recipient and recipient not in self.agent_connections[sender]:
                self.agent_connections[sender].append(recipient)
            
            # Track message count
            self.message_count[sender] = self.message_count.get(sender, 0) + 1
            
            return True
        except Exception as e:
            print(f"Error posting message from {sender}: {e}")
            return False
    
    def get_messages_for_agent(self, agent_id: str, include_broadcasts: bool = True) -> List[Message]:
        """Get all messages relevant to an agent."""
        relevant_messages = []
        
        for message in self.messages:
            # Direct messages to this agent
            if message.recipient == agent_id:
                relevant_messages.append(message)
            # Broadcast messages (if enabled)
            elif include_broadcasts and message.recipient is None and message.sender != agent_id:
                relevant_messages.append(message)
                
        return relevant_messages
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages from all agents."""
        return self.messages[-limit:] if self.messages else []
    
    def get_conversation_context_for_agent(self, agent_id: str, max_messages: int = 5) -> str:
        """Get formatted conversation context for an agent to read."""
        messages = self.get_messages_for_agent(agent_id)
        recent = messages[-max_messages:] if messages else []
        
        if not recent:
            return "No recent messages."
        
        context = "Recent messages you can see:\n"
        for msg in recent:
            if msg.recipient:
                context += f"[Direct] {msg.sender} → {msg.recipient}: {msg.content}\n"
            else:
                context += f"[Broadcast] {msg.sender}: {msg.content}\n"
        
        return context
    
    def calculate_network_centrality(self, agent_id: str) -> float:
        """Calculate network centrality for energy rewards."""
        if not self.messages:
            return 0.0
        
        # Count connections (who agent talks to + who talks to agent)
        connections = set()
        
        for message in self.messages:
            if message.sender == agent_id and message.recipient:
                connections.add(message.recipient)
            elif message.recipient == agent_id:
                connections.add(message.sender)
        
        # Centrality based on unique connections and message volume
        unique_connections = len(connections)
        message_volume = self.message_count.get(agent_id, 0)
        
        # Simple centrality score: connections + normalized message count
        centrality = unique_connections + min(message_volume / 10.0, 2.0)
        
        return centrality
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get overall communication statistics."""
        if not self.messages:
            return {"total_messages": 0, "active_agents": 0, "connections": {}}
        
        active_agents = set()
        for message in self.messages:
            active_agents.add(message.sender)
            if message.recipient:
                active_agents.add(message.recipient)
        
        return {
            "total_messages": len(self.messages),
            "active_agents": len(active_agents),
            "connections": self.agent_connections,
            "message_counts": self.message_count
        }
    
    def get_message_summary(self) -> str:
        """Get a formatted summary of recent communication."""
        stats = self.get_communication_stats()
        recent = self.get_recent_messages(5)
        
        summary = f"Communication Summary:\n"
        summary += f"  📨 Total messages: {stats['total_messages']}\n"
        summary += f"  👥 Active agents: {stats['active_agents']}\n"
        
        if recent:
            summary += f"\nRecent messages:\n"
            for msg in recent:
                if msg.recipient:
                    summary += f"  • {msg.sender} → {msg.recipient}: {msg.content[:30]}...\n"
                else:
                    summary += f"  • {msg.sender}: {msg.content[:30]}...\n"
        
        return summary 