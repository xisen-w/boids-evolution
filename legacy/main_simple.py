#!/usr/bin/env python3
"""
Simple Boids Main - Ultra Minimal Entry Point

CORE FOCUS: Just run the 3-rule boids simulation
- No energy, no survival, no marketplace complexity
- Pure research on emergent collaboration from simple rules

USAGE:
    python main_simple.py                           # 3 agents, triangle, 20 steps
    python main_simple.py --agents 4 --steps 30    # 4 agents, 30 steps
    python main_simple.py --topology line          # line topology
    python main_simple.py --quiet                  # minimal output
"""

import argparse
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simple_boids_network import SimpleBoidsNetwork


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simple Boids: Tools + Neighbors + 3 Rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main_simple.py                              # Default: 3 agents, triangle, 20 steps
    python main_simple.py --agents 4 --steps 50       # 4 agents, 50 steps
    python main_simple.py --topology line --agents 5  # Line topology with 5 agents
    python main_simple.py --topology star --agents 6  # Star topology with 6 agents
    python main_simple.py --quiet --export results.json # Quiet mode with export
        """
    )
    
    parser.add_argument(
        '--agents', '-a',
        type=int,
        default=3,
        help='Number of agents (default: 3)'
    )
    
    parser.add_argument(
        '--steps', '-s', 
        type=int,
        default=20,
        help='Number of simulation steps (default: 20)'
    )
    
    parser.add_argument(
        '--topology', '-t',
        choices=['triangle', 'line', 'star'],
        default='triangle',
        help='Network topology (default: triangle)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output mode'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export results to JSON file'
    )
    
    return parser.parse_args()


def print_banner():
    """Print the simple boids banner."""
    print("🐦" + "="*58 + "🐦")
    print("   SIMPLE BOIDS: Tools + Neighbors + 3 Rules")
    print("   Ultra minimal implementation for pure research")
    print("="*60)


def print_rules_explanation():
    """Explain the 3 boids rules."""
    print("\n🧠 THE 3 BOIDS RULES:")
    print("   1. SEPARATION:  Avoid building same tools as neighbors")
    print("   2. ALIGNMENT:   Copy successful neighbors' strategies") 
    print("   3. COHESION:    Use neighbors' tools when possible")
    print("\n🎯 RESEARCH QUESTION:")
    print("   Can these 3 simple rules create emergent specialization?")


def print_final_summary(network: SimpleBoidsNetwork):
    """Print final simulation summary."""
    summary = network.get_network_summary()
    
    print(f"\n🎉 SIMULATION COMPLETE!")
    print(f"   Total Steps: {summary['steps_completed']}")
    print(f"   Total Tools Created: {summary['total_tools']}")
    print(f"   Agent Productivity:")
    
    for agent in network.agents:
        tool_count = len(agent.tools)
        tool_types = list(set(t['type'] for t in agent.tools))
        specialization = tool_types[0] if len(tool_types) == 1 else "mixed" if tool_types else "none"
        print(f"     {agent.agent_id}: {tool_count} tools ({specialization})")


def main():
    """Main entry point for simple boids simulation."""
    args = parse_arguments()
    
    if not args.quiet:
        print_banner()
        print_rules_explanation()
    
    # Create and run simulation
    if not args.quiet:
        print(f"\n🚀 Starting simulation...")
        print(f"   Configuration: {args.agents} agents, {args.topology} topology, {args.steps} steps")
    
    network = SimpleBoidsNetwork(
        num_agents=args.agents,
        topology=args.topology
    )
    
    # Run simulation
    results = network.run_simulation(
        num_steps=args.steps,
        verbose=not args.quiet
    )
    
    # Print summary
    if not args.quiet:
        print_final_summary(network)
    
    # Export results if requested
    if args.export:
        network.export_results(args.export)
        if not args.quiet:
            print(f"📁 Results exported to {args.export}")
    
    # Return network for programmatic use
    return network, results


if __name__ == "__main__":
    main() 