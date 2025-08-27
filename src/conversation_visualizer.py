"""
Conversation Visualizer - Beautiful display of agent communications and actions.
"""
import time
from typing import Dict, Any, List
from colorama import Fore, Style, Back
from datetime import datetime


class ConversationVisualizer:
    """Visualizes agent conversations and actions in a beautiful terminal format."""
    
    def __init__(self):
        self.conversation_history = []
        self.agent_colors = {
            'Agent_01': Fore.CYAN,
            'Agent_02': Fore.MAGENTA,
            'Agent_03': Fore.YELLOW,
            'Agent_04': Fore.GREEN,
            'Agent_05': Fore.BLUE,
        }
        self.default_color = Fore.WHITE
    
    def get_agent_color(self, agent_id: str) -> str:
        """Get the color for a specific agent."""
        return self.agent_colors.get(agent_id, self.default_color)
    
    def show_agent_thinking(self, agent_id: str, context: Dict[str, Any]):
        """Show the agent's internal state before talking."""
        color = self.get_agent_color(agent_id)
        
        print(f"\n{color}🤔 {agent_id} is thinking...{Style.RESET_ALL}")
        print(f"   Energy: {context.get('energy', 0)}")
        print(f"   Available tools: {len(context.get('available_tools', []))}")
        print(f"   Success rate: {context.get('success_rate', 0):.1%}")
        
        # Add thinking animation
        for i in range(3):
            print(f"   {'.' * (i + 1)}", end='\r')
            time.sleep(0.3)
        print("   ✨")
    
    def show_agent_talk(self, agent_id: str, talk_content: str):
        """Display the agent's communication in a speech bubble style."""
        color = self.get_agent_color(agent_id)
        
        # Create speech bubble
        max_width = 60
        lines = self._wrap_text(talk_content, max_width - 4)
        
        print(f"\n{color}💬 {agent_id} says:{Style.RESET_ALL}")
        print(f"{color}┌{'─' * (max_width - 2)}┐{Style.RESET_ALL}")
        
        for line in lines:
            padding = max_width - 4 - len(line)
            print(f"{color}│ {line}{' ' * padding} │{Style.RESET_ALL}")
        
        print(f"{color}└{'─' * (max_width - 2)}┘{Style.RESET_ALL}")
    
    def show_action_parsing(self, agent_id: str, action_intent: Dict[str, Any]):
        """Show how the agent's talk is being parsed into actions."""
        color = self.get_agent_color(agent_id)
        confidence = action_intent.get('confidence', 0)
        
        print(f"\n{color}🔍 Parsing {agent_id}'s communication...{Style.RESET_ALL}")
        
        if confidence > 0.7:
            conf_color = Fore.GREEN
            conf_icon = "🎯"
        elif confidence > 0.4:
            conf_color = Fore.YELLOW
            conf_icon = "⚡"
        else:
            conf_color = Fore.RED
            conf_icon = "❓"
        
        print(f"   Tool: {action_intent.get('tool_name', 'None')}")
        print(f"   Parameters: {action_intent.get('parameters', {})}")
        print(f"   {conf_icon} Confidence: {conf_color}{confidence:.1%}{Style.RESET_ALL}")
    
    def show_action_execution(self, agent_id: str, action_result: Dict[str, Any]):
        """Display the result of the agent's action."""
        color = self.get_agent_color(agent_id)
        success = action_result.get('success', False)
        result = action_result.get('result', 'No result')
        energy_gain = action_result.get('energy_gain', 0)
        
        if success:
            status_color = Fore.GREEN
            status_icon = "✅"
        else:
            status_color = Fore.RED
            status_icon = "❌"
        
        print(f"\n{color}⚡ {agent_id}'s action result:{Style.RESET_ALL}")
        print(f"   {status_icon} {status_color}Status: {'Success' if success else 'Failed'}{Style.RESET_ALL}")
        print(f"   📝 Result: {result}")
        
        if energy_gain > 0:
            print(f"   🔋 {Fore.GREEN}Energy gained: +{energy_gain}{Style.RESET_ALL}")
        else:
            print(f"   💔 {Fore.RED}No energy gained{Style.RESET_ALL}")
    
    def show_energy_update(self, agent_id: str, old_energy: int, new_energy: int):
        """Show the agent's energy level update."""
        color = self.get_agent_color(agent_id)
        change = new_energy - old_energy
        
        if change > 0:
            change_color = Fore.GREEN
            change_icon = "📈"
            change_text = f"+{change}"
        else:
            change_color = Fore.RED
            change_icon = "📉"
            change_text = "0"
        
        print(f"   {color}{change_icon} {agent_id} Energy: {old_energy} → {change_color}{new_energy} ({change_text}){Style.RESET_ALL}")
    
    def show_cycle_summary(self, cycle_result: Dict[str, Any]):
        """Show a summary of the complete cycle."""
        agent_id = cycle_result.get('agent_id', 'Unknown')
        color = self.get_agent_color(agent_id)
        
        print(f"\n{color}📊 {agent_id} Cycle Complete{Style.RESET_ALL}")
        print(f"{color}{'─' * 30}{Style.RESET_ALL}")
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'cycle_result': cycle_result
        })
    
    def show_round_transition(self, round_num: int, total_rounds: int):
        """Show transition between simulation rounds."""
        print(f"\n{Back.BLUE}{Fore.WHITE} ROUND {round_num}/{total_rounds} COMPLETE {Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'═' * 50}{Style.RESET_ALL}")
    
    def show_agent_energy_bar(self, agent_id: str, energy: int, max_energy: int = 100):
        """Show a visual energy bar for the agent."""
        color = self.get_agent_color(agent_id)
        bar_width = 20
        filled = min(int((energy / max_energy) * bar_width), bar_width)
        empty = bar_width - filled
        
        bar = f"{'█' * filled}{'░' * empty}"
        print(f"   {color}{agent_id}: [{bar}] {energy}/{max_energy} energy{Style.RESET_ALL}")
    
    def show_society_status(self, agents_stats: Dict[str, Dict[str, Any]]):
        """Show the overall status of the agent society."""
        print(f"\n{Fore.CYAN}🏛️  SOCIETY STATUS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 40}{Style.RESET_ALL}")
        
        total_energy = sum(stats['energy'] for stats in agents_stats.values())
        total_actions = sum(stats['action_count'] for stats in agents_stats.values())
        total_successes = sum(stats['success_count'] for stats in agents_stats.values())
        
        print(f"   🔋 Total Energy: {Fore.GREEN}{total_energy}{Style.RESET_ALL}")
        print(f"   ⚡ Total Actions: {total_actions}")
        print(f"   ✅ Success Rate: {Fore.YELLOW}{total_successes/max(1, total_actions):.1%}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Individual Agents:{Style.RESET_ALL}")
        for agent_id, stats in sorted(agents_stats.items()):
            max_energy = max(agent_stats['energy'] for agent_stats in agents_stats.values())
            self.show_agent_energy_bar(agent_id, stats['energy'], max(max_energy, 50))
    
    def show_conversation_flow(self, last_n_cycles: int = 5):
        """Show the recent conversation flow between agents."""
        if not self.conversation_history:
            return
        
        print(f"\n{Fore.MAGENTA}💭 RECENT CONVERSATION FLOW{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'─' * 40}{Style.RESET_ALL}")
        
        recent = self.conversation_history[-last_n_cycles:]
        
        for i, entry in enumerate(recent):
            agent_id = entry['agent_id']
            cycle = entry['cycle_result']
            color = self.get_agent_color(agent_id)
            
            # Show abbreviated talk and result
            talk = cycle.get('talk', '')[:40] + "..." if len(cycle.get('talk', '')) > 40 else cycle.get('talk', '')
            success = "✅" if cycle.get('action_success', False) else "❌"
            energy = cycle.get('energy_gained', 0)
            
            print(f"   {color}{agent_id}:{Style.RESET_ALL} \"{talk}\" {success} (+{energy})")
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def clear_screen(self):
        """Clear the screen for a fresh display."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_tool_usage_stats(self, tool_registry):
        """Show statistics about tool usage."""
        print(f"\n{Fore.GREEN}🔧 TOOL USAGE STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'─' * 40}{Style.RESET_ALL}")
        
        # This would require the tool registry to track usage stats
        # For now, show available tools
        available_tools = tool_registry.get_available_tools()
        
        for tool_name, tool_info in available_tools.items():
            tool_type = tool_info.get('type', 'unknown')
            energy = tool_info.get('energy_reward', 0)
            type_icon = "📂" if tool_type == 'shared' else "👤"
            
            print(f"   {type_icon} {tool_name}: +{energy} energy ({tool_type})") 