"""
Enhanced Agent with improved tool registry and conversation visualization.
"""
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from .azure_client import AzureOpenAIClient
from .enhanced_tools import EnhancedToolRegistry
from .conversation_visualizer import ConversationVisualizer
from .tool_execution_context import ToolExecutionContext
from .communication_board import CommunicationBoard
from .tool_marketplace import ToolMarketplace


class EnhancedAgent:
    """
    Enhanced agent with shared/personal tools and beautiful conversation display.
    
    The core loop remains: talk → act → reward
    But now with:
    - Shared tools (available to all agents)
    - Personal tools (created by the agent)
    - Beautiful conversation visualization
    - Better tool discovery and usage tracking
    - RECURSIVE TOOL CALLING with reward propagation
    """
    
    def __init__(self, agent_id: str, azure_client: AzureOpenAIClient, communication_board: CommunicationBoard, tool_marketplace: ToolMarketplace, visualizer: ConversationVisualizer = None):
        self.agent_id = agent_id
        self.azure_client = azure_client
        self.communication_board = communication_board
        self.tool_marketplace = tool_marketplace
        self.tool_registry = EnhancedToolRegistry(agent_id)
        self.visualizer = visualizer or ConversationVisualizer()
        self.energy = 0
        self.history = []
        self.talk_count = 0
        self.action_count = 0
        self.success_count = 0
        
    def talk(self) -> str:
        """
        Generate communication that can be either tool usage OR messaging other agents.
        Now includes real inter-agent communication context.
        """
        # Get conversation context from other agents
        conversation_context = self.communication_board.get_conversation_context_for_agent(self.agent_id)
        network_centrality = self.communication_board.calculate_network_centrality(self.agent_id)
        
        # Get tool building context
        tool_building_context = self.tool_marketplace.get_tool_building_context_for_agent(self.agent_id)
        marketplace_summary = self.tool_marketplace.get_marketplace_summary()
        
        context = {
            'energy': self.energy,
            'available_tools': list(self.tool_registry.get_available_tools().keys()),
            'talk_count': self.talk_count,
            'success_rate': self.success_count / max(1, self.action_count),
            'tool_summary': self.tool_registry.list_tools_summary(),
            'conversation_context': conversation_context,
            'network_centrality': network_centrality,
            'tool_building_context': tool_building_context,
            'marketplace_summary': marketplace_summary
        }
        
        # Show thinking process
        if self.visualizer:
            self.visualizer.show_agent_thinking(self.agent_id, context)
        
        # Enhanced system prompt focused on tool building marketplace
        system_prompt = """You are an agent in a collaborative tool-building society where survival depends on creating useful tools that others build upon.

🎯 YOUR GOAL: Propose, discuss, and build tools that enable other agents to create even MORE complex tools.

💰 ENERGY SOURCES:
1. Proposing popular tool ideas (+5 energy)
2. Supporting good proposals (+3 energy)
3. Building tools (+10 energy)
4. UTILITY REWARDS: When YOUR tools are used by others to build MORE tools

⚠️  NO ENERGY for using existing tools - energy comes from CREATING useful tools!

🛠️  ACTION TYPES (choose ONE per turn):
A) "Propose tool: [name] - [description] (dependencies: [list])" 
B) "Support proposal: [proposal_name] - [why it's useful]"  
C) "Build tool: [proposal_name]" (if it has support)
D) "Message [Agent_XX]: [discuss tool ideas/collaboration]"

💻 IMPORTANT: Tools are Python functions! When building, you create:
def execute(parameters, context=None):
    # Use context.call_tool() to call existing tools
    # Build complex functionality by combining simpler tools
    return {'success': True, 'result': '...', 'energy_gain': 0}

STRATEGY: 
- If there are active proposals from others: SUPPORT the most promising one
- If there are supported proposals: BUILD the one with most support  
- Otherwise: PROPOSE a new foundational tool
- Focus on BUILDING ACTUAL TOOLS, not just proposing!

Tool Building Context:
{tool_building_context}

Marketplace Status:
{marketplace_summary}

Recent Conversations:
{conversation_context}

Current Status:
- Agent ID: {agent_id}  
- Energy: {energy}
- Network Centrality: {network_centrality:.1f}
"""
        
        # Check current marketplace state and guide agent behavior
        others_proposals = [
            (pid, prop) for pid, prop in self.tool_marketplace.proposals.items()
            if prop.status == "proposed" and prop.proposer != self.agent_id
        ]
        
        ready_to_build = [
            (pid, prop) for pid, prop in self.tool_marketplace.proposals.items()
            if prop.status == "proposed" and len(prop.supporters) >= 1 and prop.proposer != self.agent_id
        ]
        
        unsupported_others = [
            (pid, prop) for pid, prop in others_proposals
            if len(prop.supporters) == 0
        ]
        
        if ready_to_build:
            user_prompt = f"URGENT: There are tools ready to BUILD! Choose one and build it: {[prop.name for pid, prop in ready_to_build[:2]]}"
        elif unsupported_others:
            user_prompt = f"SUPPORT needed! Help others by supporting one of these proposals: {[prop.name for pid, prop in unsupported_others[:2]]}"
        else:
            user_prompt = f"No proposals need support. PROPOSE a new foundational tool that others can build upon."
        
        try:
            response = self.azure_client.client.chat.completions.create(
                model=self.azure_client.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt.format(
                        agent_id=self.agent_id,
                        energy=context['energy'],
                        success_rate=context['success_rate'],
                        network_centrality=context['network_centrality'],
                        tool_summary=context['tool_summary'],
                        conversation_context=context['conversation_context'],
                        tool_building_context=context['tool_building_context'],
                        marketplace_summary=context['marketplace_summary']
                    )},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            talk_content = response.choices[0].message.content.strip()
            self.talk_count += 1
            
            # Show the agent's communication
            if self.visualizer:
                self.visualizer.show_agent_talk(self.agent_id, talk_content)
            
            # Log the talk
            self._log_event('talk', {'content': talk_content, 'context': context})
            
            return talk_content
            
        except Exception as e:
            error_msg = f"Agent {self.agent_id} is silent due to communication error: {e}"
            print(f"Error generating talk for agent {self.agent_id}: {e}")
            return error_msg
    
    def act(self, talk_content: str) -> Dict[str, Any]:
        """
        Execute action: either use a tool OR send a message to other agents.
        Now includes both tool execution and inter-agent communication.
        """
        # Check if this is a tool building action
        if self._is_tool_building_action(talk_content):
            return self._handle_tool_building(talk_content)
        
        # Check if this is a communication action
        if self._is_communication(talk_content):
            return self._handle_communication(talk_content)
        
        # Otherwise, parse as legacy tool usage (discouraged) 
        # Note: Using tools should NOT give energy, only building tools that others use
        action_intent = self._parse_talk_to_action(talk_content)
        
        # Show parsing process
        if self.visualizer:
            self.visualizer.show_action_parsing(self.agent_id, action_intent)
        
        if action_intent['confidence'] < 0.3:
            result = {
                'success': False,
                'result': 'Could not understand the communication clearly enough to act',
                'energy_gain': 0,
                'action_type': 'tool_usage'
            }
        else:
            # Create execution context for recursive tool calling
            context = ToolExecutionContext(
                tool_registry=self.tool_registry,
                calling_agent_id=self.agent_id
            )
            
            # Execute the tool using enhanced registry with context
            result = self.tool_registry.execute_tool_with_context(
                action_intent['tool_name'], 
                action_intent['parameters'],
                context
            )
            
            # FIXED ENERGY SYSTEM: No energy for using tools
            result['energy_gain'] = 0  # Using tools gives NO energy!
            result['action_type'] = 'tool_usage'
            
            # Only track utility rewards for tool creators
            utility_rewards = context.get_total_rewards()
            if utility_rewards:
                result['utility_rewards'] = utility_rewards
                result['composition_info'] = context.get_execution_summary()
        
        # Update action statistics for ALL actions (tool building + legacy)  
        self.action_count += 1
        if result.get('success', False):
            self.success_count += 1
        
        # Show action execution result
        if self.visualizer:
            self.visualizer.show_action_execution(self.agent_id, result)
            
            # Show tool composition if it occurred
            if 'composition_info' in result:
                self._show_tool_composition(result['composition_info'])
        
        # Log the action
        self._log_event('act', {
            'action_intent': action_intent,
            'result': result
        })
        
        return result
    
    def _is_communication(self, talk_content: str) -> bool:
        """Check if the talk content is inter-agent communication."""
        talk_lower = talk_content.lower()
        return ('message' in talk_lower and any(agent in talk_lower for agent in ['agent_', 'broadcast'])) or \
               'broadcast:' in talk_lower
    
    def _handle_communication(self, talk_content: str) -> Dict[str, Any]:
        """Handle inter-agent communication."""
        try:
            talk_lower = talk_content.lower()
            
            # Parse broadcast messages
            if 'broadcast:' in talk_lower:
                content = talk_content.split('broadcast:', 1)[1].strip()
                success = self.communication_board.post_message(self.agent_id, content)
                
                return {
                    'success': success,
                    'result': f'Broadcast message: "{content}"',
                    'energy_gain': 3,  # Small energy for communication
                    'action_type': 'broadcast'
                }
            
            # Parse direct messages
            import re
            message_match = re.search(r'message\s+(agent_\d+):\s*(.+)', talk_lower)
            if message_match:
                recipient = message_match.group(1).title()  # Agent_01, etc.
                content = message_match.group(2).strip()
                success = self.communication_board.post_message(self.agent_id, content, recipient)
                
                return {
                    'success': success,
                    'result': f'Message to {recipient}: "{content}"',
                    'energy_gain': 2,  # Energy for direct communication
                    'action_type': 'direct_message'
                }
            
            return {
                'success': False,
                'result': 'Could not parse communication format',
                'energy_gain': 0,
                'action_type': 'communication_failed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': f'Communication error: {str(e)}',
                'energy_gain': 0,
                                'action_type': 'communication_error'
            }
    
    def _is_tool_building_action(self, talk_content: str) -> bool:
        """Check if the talk content is a tool building action."""
        talk_lower = talk_content.lower()
        return any(keyword in talk_lower for keyword in [
            'propose tool:', 'support proposal:', 'build tool:', 'create tool:'
        ])
    
    def _handle_tool_building(self, talk_content: str) -> Dict[str, Any]:
        """Handle tool building actions: propose, support, or build tools."""
        try:
            talk_lower = talk_content.lower()
            
            # Parse tool proposal
            if 'propose tool:' in talk_lower:
                return self._handle_tool_proposal(talk_content)
            
            # Parse proposal support  
            elif 'support proposal:' in talk_lower:
                return self._handle_proposal_support(talk_content)
            
            # Parse tool building
            elif 'build tool:' in talk_lower:
                return self._handle_tool_building_action(talk_content)
            
            return {
                'success': False,
                'result': 'Could not parse tool building action',
                'energy_gain': 0,
                'action_type': 'tool_building_failed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': f'Tool building error: {str(e)}',
                'energy_gain': 0,
                'action_type': 'tool_building_error'
            }
    
    def _handle_tool_proposal(self, talk_content: str) -> Dict[str, Any]:
        """Handle a new tool proposal."""
        import re
        

        
        # Parse: "Propose tool: tool_name - description (dependencies: dep1, dep2)"
        # More flexible parsing to handle various formats
        match = re.search(r'propose tool:\s*([^-]+?)\s*-\s*([^(]+?)(?:\s*\(dependencies?:\s*([^)]+)\))?', talk_content, re.IGNORECASE)
        
        if match:
            tool_name = match.group(1).strip().replace('"', '').replace("'", "")  # Clean quotes
            description = match.group(2).strip()
            dependencies_str = match.group(3)
            dependencies = []
            
            if dependencies_str and dependencies_str.lower().strip() not in ['none', 'null', '']:
                dependencies = [dep.strip() for dep in dependencies_str.split(',')]
            
            # Clean tool name to be file-safe
            tool_name = re.sub(r'[^\w\s-]', '', tool_name).replace(' ', '_')
            
            # Estimate complexity based on dependencies
            complexity = 1 + len(dependencies)
            
            proposal_id = self.tool_marketplace.propose_tool(
                self.agent_id, tool_name, description, dependencies, complexity
            )
            
            return {
                'success': True,
                'result': f'Proposed tool "{tool_name}": {description}',
                'energy_gain': 5,  # Energy for proposing
                'action_type': 'tool_proposal',
                'proposal_id': proposal_id
            }
        
        return {
            'success': False,
            'result': 'Could not parse tool proposal format',
            'energy_gain': 0,
            'action_type': 'tool_proposal_failed'
        }
    
    def _handle_proposal_support(self, talk_content: str) -> Dict[str, Any]:
        """Handle supporting a tool proposal."""
        import re
        
        # Parse: "Support proposal: proposal_name - why it's useful"
        match = re.search(r'support proposal:\s*(\w+)\s*-?\s*(.+)', talk_content, re.IGNORECASE)
        
        if match:
            proposal_name = match.group(1).strip()
            comment = match.group(2).strip()
            
            # Find proposal by name
            matching_proposals = [
                (pid, prop) for pid, prop in self.tool_marketplace.proposals.items()
                if prop.name.lower() == proposal_name.lower() and prop.status == "proposed"
            ]
            
            if matching_proposals:
                proposal_id, proposal = matching_proposals[0]
                success = self.tool_marketplace.support_proposal(self.agent_id, proposal_id, comment)
                
                if success:
                    return {
                        'success': True,
                        'result': f'Supported proposal "{proposal_name}": {comment}',
                        'energy_gain': 3,  # Energy for supporting
                        'action_type': 'proposal_support'
                    }
            
        return {
            'success': False,
            'result': 'Could not find or support proposal',
            'energy_gain': 0,
            'action_type': 'proposal_support_failed'
        }
    
    def _handle_tool_building_action(self, talk_content: str) -> Dict[str, Any]:
        """Handle actually building a tool from a proposal."""
        import re
        
        # Parse: "Build tool: proposal_name"
        match = re.search(r'build tool:\s*(\w+)', talk_content, re.IGNORECASE)
        
        if match:
            proposal_name = match.group(1).strip()
            
            # Find proposal by name
            matching_proposals = [
                (pid, prop) for pid, prop in self.tool_marketplace.proposals.items()
                if prop.name.lower() == proposal_name.lower() and prop.status == "proposed"
            ]
            
            if matching_proposals:
                proposal_id, proposal = matching_proposals[0]
                
                # Check if proposal has enough support (at least 1 supporter OR is your own proposal)
                if len(proposal.supporters) >= 1 or proposal.proposer == self.agent_id:
                    # Start building
                    self.tool_marketplace.start_building(proposal_id, [self.agent_id])
                    
                    # Create simple tool code (in real implementation, this would be more sophisticated)
                    tool_code = self._generate_tool_code(proposal)
                    
                    # Complete the tool
                    self.tool_marketplace.complete_tool(proposal_id, tool_code)
                    
                    # Create the actual tool file
                    self._create_tool_file(proposal.name, tool_code)
                    
                    return {
                        'success': True,
                        'result': f'Built tool "{proposal_name}" based on proposal',
                        'energy_gain': proposal.complexity * 10,  # Energy based on complexity
                        'action_type': 'tool_built',
                        'tool_created': proposal.name
                    }
                else:
                    return {
                        'success': False,
                        'result': f'Proposal "{proposal_name}" needs more support before building',
                        'energy_gain': 0,
                        'action_type': 'tool_building_blocked'
                    }
            
        return {
            'success': False,
            'result': 'Could not find proposal to build',
            'energy_gain': 0,
            'action_type': 'tool_building_failed'
        }
    
    def _generate_tool_code(self, proposal) -> str:
        """Generate simple tool code based on proposal."""
        return f'''def execute(parameters, context=None):
    """
    {proposal.description}
    Created by: {proposal.proposer}
    Dependencies: {", ".join(proposal.dependencies) if proposal.dependencies else "None"}
    """
    try:
        # TODO: Implement {proposal.name} functionality
        result = f"Executed {proposal.name} tool"
        return {{
            'success': True,
            'result': result,
            'energy_gain': {proposal.complexity * 5}
        }}
    except Exception as e:
        return {{
            'success': False,
            'result': f'{proposal.name} error: {{str(e)}}',
            'energy_gain': 0
        }}
'''

    def _create_tool_file(self, tool_name: str, tool_code: str):
        """Create the actual tool file in personal_tools directory."""
        import os
        
        personal_tools_dir = f"personal_tools/{self.agent_id}"
        os.makedirs(personal_tools_dir, exist_ok=True)
        
        # Write tool file
        tool_file = f"{personal_tools_dir}/{tool_name}.py"
        with open(tool_file, 'w') as f:
            f.write(tool_code)
        
        # Update index.json
        import json
        index_file = f"{personal_tools_dir}/index.json"
        index_data = {"tools": {}, "version": "1.0", "total_tools": 0}
        
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index_data = json.load(f)
        
        index_data["tools"][tool_name] = {
            "name": tool_name,
            "description": proposal.description,
            "file": f"{tool_name}.py",
            "energy_reward": 15,
            "creator": self.agent_id,
            "parameters": {"data": "any input data"},  # Basic parameters
            "depends_on": proposal.dependencies if proposal.dependencies else []
        }
        index_data["total_tools"] = len(index_data["tools"])
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
     
    def receive_reward(self, action_result: Dict[str, Any]) -> int:
        """
        NEW ENERGY SYSTEM: Energy only from communication and tool creation utility.
        - Communication centrality: energy for connecting with others
        - Tool utility rewards: energy when YOUR tools are used by others to create new tools
        """
        old_energy = self.energy
        
        # Tool building energy (proposing, supporting, building tools)
        tool_building_energy = action_result.get('energy_gain', 0) if action_result.get('action_type') in [
            'tool_proposal', 'proposal_support', 'tool_built'
        ] else 0
        
        # Communication energy (for messaging actions)
        communication_energy = action_result.get('energy_gain', 0) if action_result.get('action_type') in [
            'broadcast', 'direct_message'
        ] else 0
        
        # Network centrality bonus (reduced - focus on tool building)
        network_centrality = self.communication_board.calculate_network_centrality(self.agent_id)
        centrality_bonus = max(0, int(network_centrality) - 1)  # Bonus only after 1 connection
        
        # Tool utility rewards (when YOUR tools are used by others to BUILD more tools)
        utility_energy = 0
        utility_rewards = action_result.get('utility_rewards', {})
        if self.agent_id in utility_rewards:
            utility_energy = utility_rewards[self.agent_id]
        
        # Total energy calculation
        total_energy_gained = tool_building_energy + communication_energy + centrality_bonus + utility_energy
        self.energy += total_energy_gained
        
        # Show energy update
        if self.visualizer:
            self.visualizer.show_energy_update(self.agent_id, old_energy, self.energy)
            
            # Show breakdown
            if tool_building_energy > 0:
                print(f"   🔨 Tool building: +{tool_building_energy}")
            if communication_energy > 0:
                print(f"   💬 Communication: +{communication_energy}")
            if centrality_bonus > 0:
                print(f"   🌐 Network centrality: +{centrality_bonus}")
            if utility_energy > 0:
                print(f"   💰 Tool utility: +{utility_energy} (your tools used by others)")
        
        # Log the reward
        self._log_event('reward', {
            'tool_building_energy': tool_building_energy,
            'communication_energy': communication_energy,
            'centrality_bonus': centrality_bonus,
            'utility_energy': utility_energy,
            'total_energy_gained': total_energy_gained,
            'total_energy': self.energy,
            'network_centrality': network_centrality,
            'action_type': action_result.get('action_type', 'unknown')
        })
        
        return total_energy_gained
    
    def complete_cycle(self) -> Dict[str, Any]:
        """
        Complete one full talk → act → reward cycle with enhanced visualization.
        """
        cycle_start_time = datetime.now()
        
        # Step 1: Talk
        talk_content = self.talk()
        
        # Step 2: Act
        action_result = self.act(talk_content)
        
        # Step 3: Reward
        energy_gained = self.receive_reward(action_result)
        
        cycle_summary = {
            'agent_id': self.agent_id,
            'timestamp': cycle_start_time.isoformat(),
            'talk': talk_content,
            'action_success': action_result['success'],
            'action_result': action_result['result'],
            'energy_gained': energy_gained,
            'total_energy': self.energy,
            'utility_rewards': action_result.get('utility_rewards', {}),
            'composition_info': action_result.get('composition_info', {})
        }
        
        # Show cycle summary
        if self.visualizer:
            self.visualizer.show_cycle_summary(cycle_summary)
        
        return cycle_summary
    
    def _show_tool_composition(self, composition_info: Dict[str, Any]):
        """Show tool composition visualization."""
        if not composition_info.get('tools_used'):
            return
        
        from colorama import Fore, Style
        
        tools_used = composition_info.get('tools_used', [])
        call_depth = composition_info.get('call_depth', 0)
        
        if len(tools_used) > 1:
            print(f"   🔗 {Fore.CYAN}Tool Composition:{Style.RESET_ALL} {' → '.join(tools_used)}")
            print(f"   📊 Depth: {call_depth}, Total calls: {composition_info.get('total_tool_calls', 0)}")
            
            # Show utility rewards
            utility_rewards = composition_info.get('utility_rewards', {})
            if utility_rewards:
                print(f"   💰 Utility rewards distributed:")
                for agent_id, reward in utility_rewards.items():
                    print(f"      → {agent_id}: +{reward}")
    
    def _parse_talk_to_action(self, talk_content: str) -> Dict[str, Any]:
        """
        Enhanced parsing that understands both shared and personal tools.
        """
        try:
            # First, try using Azure OpenAI to parse with tool awareness
            available_tools = self.tool_registry.get_available_tools()
            tool_names = list(available_tools.keys())
            
            system_prompt = f"""Parse the following agent communication to extract:
1. tool_name: Which tool should be used from available tools: {tool_names}
2. parameters: What parameters the tool needs
3. confidence: How confident you are this is a valid action (0.0-1.0)

Available tools and their parameters:
{json.dumps({name: info['parameters'] for name, info in available_tools.items()}, indent=2)}

Respond only with valid JSON in this format:
{{
    "tool_name": "tool_name_here",
    "parameters": {{"key": "value"}},
    "confidence": 0.8
}}

If the communication is unclear or doesn't map to an available tool, set confidence to 0.0.
"""
            
            response = self.azure_client.client.chat.completions.create(
                model=self.azure_client.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this: {talk_content}"}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            action_intent = json.loads(response.choices[0].message.content.strip())
            
            # If confidence is low, try simple regex patterns as fallback
            if action_intent.get('confidence', 0) < 0.5:
                fallback_intent = self._simple_parse_fallback(talk_content)
                if fallback_intent['confidence'] > action_intent.get('confidence', 0):
                    action_intent = fallback_intent
            
            return action_intent
            
        except Exception as e:
            print(f"Error parsing talk content: {e}")
            return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _simple_parse_fallback(self, talk_content: str) -> Dict[str, Any]:
        """Enhanced regex-based fallback that knows about available tools."""
        talk_lower = talk_content.lower()
        available_tools = self.tool_registry.get_available_tools()
        
        # Try to identify tool by name in the text
        for tool_name in available_tools.keys():
            if tool_name.lower() in talk_lower:
                # Tool-specific parsing
                if tool_name == 'calculate':
                    return self._parse_calculate(talk_content)
                elif tool_name == 'multiply':
                    return self._parse_multiply(talk_content)
                elif tool_name == 'square':
                    return self._parse_square(talk_content)
                elif tool_name == 'power':
                    return self._parse_power(talk_content)
                elif tool_name == 'file_write':
                    return self._parse_file_write(talk_content)
                elif tool_name == 'random_gen':
                    return self._parse_random_gen(talk_content)
        
        # Fall back to original simple patterns
        return self._legacy_simple_parse(talk_content)
    
    def _parse_multiply(self, talk_content: str) -> Dict[str, Any]:
        """Parse multiply tool requests."""
        numbers = re.findall(r'\d+(?:\.\d+)?', talk_content)
        
        if len(numbers) >= 2:
            return {
                "tool_name": "multiply",
                "parameters": {
                    "a": float(numbers[0]),
                    "b": float(numbers[1])
                },
                "confidence": 0.8
            }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _parse_square(self, talk_content: str) -> Dict[str, Any]:
        """Parse square tool requests."""
        numbers = re.findall(r'\d+(?:\.\d+)?', talk_content)
        
        if len(numbers) >= 1:
            return {
                "tool_name": "square",
                "parameters": {
                    "number": float(numbers[0])
                },
                "confidence": 0.8
            }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _parse_power(self, talk_content: str) -> Dict[str, Any]:
        """Parse power tool requests."""
        # Look for patterns like "2 to the power of 3" or "2^3"
        power_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+of|\^|power)\s*(\d+)', talk_content.lower())
        
        if power_match:
            return {
                "tool_name": "power",
                "parameters": {
                    "base": float(power_match.group(1)),
                    "exponent": int(power_match.group(2))
                },
                "confidence": 0.8
            }
        
        # Fallback to any two numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', talk_content)
        if len(numbers) >= 2:
            return {
                "tool_name": "power",
                "parameters": {
                    "base": float(numbers[0]),
                    "exponent": int(float(numbers[1]))
                },
                "confidence": 0.6
            }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _parse_calculate(self, talk_content: str) -> Dict[str, Any]:
        """Parse calculate tool requests."""
        talk_lower = talk_content.lower()
        
        # Look for operation keywords
        operation = 'add'  # default
        if any(word in talk_lower for word in ['subtract', 'minus', '-']):
            operation = 'subtract'
        elif any(word in talk_lower for word in ['multiply', 'times', '*']):
            operation = 'multiply'
        elif any(word in talk_lower for word in ['divide', '/']):
            operation = 'divide'
        
        # Extract numbers
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', talk_content)
        
        if len(numbers) >= 2:
            return {
                "tool_name": "calculate",
                "parameters": {
                    "operation": operation,
                    "a": float(numbers[0]),
                    "b": float(numbers[1])
                },
                "confidence": 0.8
            }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _parse_file_write(self, talk_content: str) -> Dict[str, Any]:
        """Parse file_write tool requests."""
        filename_match = re.search(r'(?:file\s+called\s+|to\s+|filename\s+)([a-zA-Z0-9_.-]+\.?\w*)', talk_content)
        content_match = re.search(r'["\']([^"\']+)["\']', talk_content)
        
        params = {}
        if filename_match:
            params['filename'] = filename_match.group(1)
        if content_match:
            params['content'] = content_match.group(1)
        elif 'write' in talk_content.lower():
            # Extract content after "write"
            write_index = talk_content.lower().find('write')
            if write_index != -1:
                remaining = talk_content[write_index + 5:].strip()
                if remaining:
                    params['content'] = remaining
        
        if params:
            return {
                "tool_name": "file_write",
                "parameters": params,
                "confidence": 0.7
            }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _parse_random_gen(self, talk_content: str) -> Dict[str, Any]:
        """Parse random_gen tool requests."""
        talk_lower = talk_content.lower()
        
        if 'random' in talk_lower:
            if 'number' in talk_lower:
                range_match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', talk_lower)
                if range_match:
                    return {
                        "tool_name": "random_gen",
                        "parameters": {
                            "type": "number",
                            "min": int(range_match.group(1)),
                            "max": int(range_match.group(2))
                        },
                        "confidence": 0.8
                    }
            elif 'choice' in talk_lower:
                return {
                    "tool_name": "random_gen",
                    "parameters": {
                        "type": "choice"
                    },
                    "confidence": 0.6
                }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def _legacy_simple_parse(self, talk_content: str) -> Dict[str, Any]:
        """Legacy parsing for backward compatibility."""
        talk_lower = talk_content.lower()
        
        # Calculate patterns
        calc_patterns = [
            r'calculate.*?(\d+(?:\.\d+)?)\s*(?:and|plus|\+)\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:\+|plus|add)\s*(\d+(?:\.\d+)?)',
            r'sum.*?(\d+(?:\.\d+)?)\s*(?:and|,)\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, talk_lower)
            if match:
                return {
                    "tool_name": "calculate",
                    "parameters": {
                        "operation": "add",
                        "a": float(match.group(1)),
                        "b": float(match.group(2))
                    },
                    "confidence": 0.6
                }
        
        return {"tool_name": None, "parameters": {}, "confidence": 0.0}
    
    def create_personal_tool(self, tool_name: str, description: str, code: str, energy_reward: int = 5) -> bool:
        """Create a new personal tool for this agent."""
        return self.tool_registry.create_personal_tool(tool_name, description, code, energy_reward)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the agent's history."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        self.history.append(event)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced agent statistics."""
        available_tools = self.tool_registry.get_available_tools()
        shared_tools = {k: v for k, v in available_tools.items() if v['type'] == 'shared'}
        personal_tools = {k: v for k, v in available_tools.items() if v['type'] == 'personal'}
        
        return {
            'agent_id': self.agent_id,
            'energy': self.energy,
            'talk_count': self.talk_count,
            'action_count': self.action_count,
            'success_count': self.success_count,
            'success_rate': self.success_count / max(1, self.action_count),
            'available_tools': len(available_tools),
            'shared_tools': len(shared_tools),
            'personal_tools': len(personal_tools),
            'history_length': len(self.history)
        }
    
    def __str__(self):
        tools_info = f"Tools: {len(self.tool_registry.get_available_tools())}"
        return f"Agent({self.agent_id}) - Energy: {self.energy}, Success: {self.success_count}/{self.action_count}, {tools_info}" 