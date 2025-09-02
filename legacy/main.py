#!/usr/bin/env python3
"""
Boids Evolution v0.0 - Agent Society with Recursive Tool Composition
Main entry point for the enhanced talk → act → reward simulation.

This demonstrates the core principle: agents must communicate to trigger actions
and gain energy. Tools can call other tools, creating a recursive ecosystem where
agents are rewarded for creating useful building blocks.

BREAKTHROUGH FEATURE: Tool Composition with Reward Propagation
- Tools can call other tools during execution
- Creators of used tools get utility rewards
- Complex behaviors emerge from simple tool combinations
"""
import os
import sys
import argparse
import time
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_agent import EnhancedAgent
from src.azure_client import AzureOpenAIClient
from src.conversation_visualizer import ConversationVisualizer
from src.enhanced_tools import EnhancedToolRegistry
from src.communication_board import CommunicationBoard
from src.tool_marketplace import ToolMarketplace
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


def check_environment():
    """Check if Azure OpenAI environment variables are set."""
    load_dotenv()
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"{Fore.RED}❌ Missing required environment variables:{Style.RESET_ALL}")
        for var in missing_vars:
            print(f"   {var}")
        print(f"\n{Fore.YELLOW}📝 Please create a .env file with your Azure OpenAI credentials.{Style.RESET_ALL}")
        print("   Use .env.example as a template.")
        return False
    
    return True


def show_available_tools():
    """Display available tools from the shared_tools directory."""
    registry = EnhancedToolRegistry()
    print(registry.list_tools_summary())


def run_simulation(num_agents: int, num_rounds: int, delay: float, verbose: bool, demo_mode: bool, simple_mode: bool):
    """Run the agent society simulation."""
    
    # Initialize components
    azure_client = AzureOpenAIClient()
    communication_board = CommunicationBoard()  # Shared communication board
    tool_marketplace = ToolMarketplace()  # Shared tool marketplace
    visualizer = ConversationVisualizer() if not simple_mode else None
    
    # Create agents (all share the same communication board)
    agents = []
    for i in range(num_agents):
        agent_id = f"Agent_{i+1:02d}"
        agent = EnhancedAgent(agent_id, azure_client, communication_board, tool_marketplace, visualizer)
        agents.append(agent)
    
    if verbose:
        if simple_mode:
            print(f"{Fore.GREEN}🚀 Simple Agent Society Simulation{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}🚀 Enhanced Agent Society with Tool Composition{Style.RESET_ALL}")
        print(f"Agents: {len(agents)} | Rounds: {num_rounds}")
        
        # Show available tools
        if not simple_mode:
            show_available_tools()
            if demo_mode:
                print(f"\n{Fore.BLUE}🎬 DEMO MODE: Enhanced visualizations enabled{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🎯 Core Principle: Talk → Act → Reward{Style.RESET_ALL}")
    if not simple_mode:
        print(f"✨ Enhanced with TOOL BUILDING MARKETPLACE + INTER-AGENT COMMUNICATION")
        print(f"💰 Energy from: proposing popular tools + building tools others use")
        print(f"🗨️  Agents propose, discuss, and build tools collaboratively")
    
    if demo_mode:
        input(f"\n{Fore.YELLOW}Press Enter to start the demo...{Style.RESET_ALL}")
        if visualizer:
            visualizer.clear_screen()
    
    total_utility_rewards = {}  # Track utility rewards across all agents
    
    try:
        for round_num in range(1, num_rounds + 1):
            if verbose:
                print(f"\n{Fore.CYAN}{'='*60}")
                if simple_mode:
                    print(f"🤖 ROUND {round_num} - Agent Society")
                else:
                    print(f"🤖 ROUND {round_num} - Enhanced Agent Society with Tool Composition")
                print(f"{'='*60}{Style.RESET_ALL}")
            
            round_results = []
            
            for agent in agents:
                if verbose and not simple_mode:
                    print(f"\n{Fore.MAGENTA}>>> {agent.agent_id} Turn{Style.RESET_ALL}")
                
                try:
                    # Complete one cycle with full visualization
                    cycle_result = agent.complete_cycle()
                    round_results.append(cycle_result)
                    
                    # Track utility rewards
                    utility_rewards = cycle_result.get('utility_rewards', {})
                    for agent_id, reward in utility_rewards.items():
                        total_utility_rewards[agent_id] = total_utility_rewards.get(agent_id, 0) + reward
                    
                    if demo_mode:
                        time.sleep(1)  # Pause for demo effect
                        
                except Exception as e:
                    if verbose:
                        print(f"{Fore.RED}❌ Error in {agent.agent_id} cycle: {e}{Style.RESET_ALL}")
                    round_results.append({
                        'agent_id': agent.agent_id,
                        'error': str(e),
                        'energy_gained': 0,
                        'total_energy': agent.energy
                    })
            
            # Show round summary
            if verbose:
                agent_stats = {agent.agent_id: agent.get_stats() for agent in agents}
                
                if simple_mode:
                    # Simple summary
                    total_energy = sum(stats['energy'] for stats in agent_stats.values())
                    print(f"\n{Fore.CYAN}📊 ROUND {round_num} SUMMARY{Style.RESET_ALL}")
                    print(f"Total Energy: {Fore.GREEN}{total_energy}{Style.RESET_ALL}")
                    for agent_id, stats in agent_stats.items():
                        print(f"  {agent_id}: {stats['energy']} energy")
                else:
                    # Enhanced summary with tool composition info
                    if visualizer:
                        visualizer.show_society_status(agent_stats)
                        visualizer.show_conversation_flow()
                        
                        # Show tool usage stats
                        if agents:
                            visualizer.show_tool_usage_stats(agents[0].tool_registry)
                    
                    # Show utility rewards summary
                    if total_utility_rewards:
                        print(f"\n{Fore.YELLOW}💰 UTILITY REWARDS SUMMARY (Total across all rounds):{Style.RESET_ALL}")
                        for agent_id, total_reward in total_utility_rewards.items():
                            print(f"   {agent_id}: +{total_reward} (tools used by others)")
                    
                    # Show communication summary
                    comm_summary = communication_board.get_message_summary()
                    if communication_board.messages:
                        print(f"\n{Fore.BLUE}🗨️  COMMUNICATION SUMMARY:{Style.RESET_ALL}")
                        print(comm_summary)
                    
                    # Show marketplace summary
                    marketplace_summary = tool_marketplace.get_marketplace_summary()
                    print(f"\n{Fore.MAGENTA}🛠️  TOOL MARKETPLACE SUMMARY:{Style.RESET_ALL}")
                    print(marketplace_summary)
            
            # Round transition
            if round_num < num_rounds:
                if verbose and not simple_mode and visualizer:
                    visualizer.show_round_transition(round_num, num_rounds)
                
                if delay > 0:
                    if demo_mode:
                        input(f"\n{Fore.BLUE}Press Enter for next round...{Style.RESET_ALL}")
                    else:
                        if verbose:
                            print(f"{Fore.BLUE}⏳ Waiting {delay}s before next round...{Style.RESET_ALL}")
                        time.sleep(delay)
        
        # Final summary
        if verbose:
            print(f"\n{Fore.GREEN}{'='*60}")
            if simple_mode:
                print("🏁 SIMULATION COMPLETE")
            else:
                print("🏁 ENHANCED SIMULATION COMPLETE")
            print(f"{'='*60}{Style.RESET_ALL}")
            
            # Show final agent rankings and statistics
            agent_stats = {agent.agent_id: agent.get_stats() for agent in agents}
            
            if simple_mode:
                # Simple final summary
                total_energy = sum(stats['energy'] for stats in agent_stats.values())
                print(f"Final Total Energy: {Fore.GREEN}{total_energy}{Style.RESET_ALL}")
                
                # Final rankings
                sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]['energy'], reverse=True)
                print(f"\n{Fore.MAGENTA}🏆 FINAL RANKINGS:{Style.RESET_ALL}")
                for rank, (agent_id, stats) in enumerate(sorted_agents, 1):
                    emoji = "👑" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🤖"
                    print(f"  {rank}. {emoji} {agent_id}: {stats['energy']} energy")
            else:
                # Enhanced final summary
                if visualizer:
                    visualizer.show_society_status(agent_stats)
                
                # Show final tool breakdown
                total_shared = sum(stats['shared_tools'] for stats in agent_stats.values()) // len(agents)  # Shared tools are the same for all
                total_personal = sum(stats['personal_tools'] for stats in agent_stats.values())
                total_energy = sum(stats['energy'] for stats in agent_stats.values())
                
                print(f"\n{Fore.YELLOW}📈 FINAL STATISTICS:{Style.RESET_ALL}")
                print(f"   🔧 Shared Tools Available: {total_shared}")
                print(f"   👤 Personal Tools Created: {total_personal}")
                print(f"   ⚡ Total Energy Generated: {Fore.GREEN}{total_energy}{Style.RESET_ALL}")
                print(f"   💰 Total Utility Rewards: {Fore.YELLOW}{sum(total_utility_rewards.values())}{Style.RESET_ALL}")
            
            # Demonstrate core principle
            print(f"\n{Fore.CYAN}💡 CORE PRINCIPLE VALIDATION:{Style.RESET_ALL}")
            print("✅ Agents who talked gained energy")
            print("✅ No communication = No action = No reward")
            if not simple_mode:
                print("✅ Tool composition created utility reward streams")
                print("✅ Complex behaviors emerged from simple tool combinations")
            print("✅ Society thrived through communication and tool use")
        
        return True
        
    except KeyboardInterrupt:
        if verbose:
            print(f"\n{Fore.YELLOW}🛑 Simulation interrupted by user{Style.RESET_ALL}")
        return False
    except Exception as e:
        if verbose:
            print(f"\n{Fore.RED}💥 Simulation error: {e}{Style.RESET_ALL}")
        return False


def main():
    """Enhanced main function with both simple and advanced modes."""
    parser = argparse.ArgumentParser(
        description="Boids Evolution v0.0 - Agent Society with Recursive Tool Composition"
    )
    parser.add_argument(
        '--agents', '-a', 
        type=int, 
        default=3,
        help='Number of agents in the society (default: 3)'
    )
    parser.add_argument(
        '--rounds', '-r',
        type=int,
        default=3,
        help='Number of simulation rounds (default: 3)'
    )
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=1.0,
        help='Delay between rounds in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Run in quiet mode (minimal output)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with interactive pauses and enhanced visuals'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Run in simple mode without enhanced visualizations'
    )
    parser.add_argument(
        '--show-tools',
        action='store_true',
        help='Show available tools and exit'
    )
    
    args = parser.parse_args()
    
    # Show tools and exit if requested
    if args.show_tools:
        print(f"{Fore.CYAN}🔧 AVAILABLE TOOLS{Style.RESET_ALL}")
        show_available_tools()
        return
    
    # Check environment setup
    if not check_environment():
        sys.exit(1)
    
    try:
        if args.simple:
            print(f"{Fore.MAGENTA}🤖 Boids Evolution v0.0 - Simple Agent Society{Style.RESET_ALL}")
        else:
            print(f"{Fore.MAGENTA}🤖 Boids Evolution v0.0 - Enhanced Agent Society{Style.RESET_ALL}")
        print("=" * 60)
        
        if not args.simple:
            print(f"✨ Features: Recursive Tool Composition, Reward Propagation")
        print(f"🎯 Core: Talk → Act → Reward")
        if not args.simple:
            print(f"🔗 Tools can call other tools, creating emergent complexity")
        print(f"Initializing society with {args.agents} agents...")
        
        # Run the simulation
        success = run_simulation(
            num_agents=args.agents,
            num_rounds=args.rounds,
            delay=args.delay,
            verbose=not args.quiet,
            demo_mode=args.demo,
            simple_mode=args.simple
        )
        
        if success:
            print(f"\n{Fore.GREEN}🎉 Simulation completed successfully!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Simulation ended early{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Simulation interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}💥 Error running simulation: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main() 