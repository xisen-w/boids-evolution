#!/usr/bin/env python3
"""
Main entry point for PROPER Tool Boids simulation.

REAL COMPUTATIONAL TOOLS: Fibonacci, Prime checking, Statistics, Palindromes, etc.
NO MORE WRAPPER FUNCTIONS: Each tool is a unique computational algorithm.
"""

import argparse
import json
import os
from datetime import datetime

from src.proper_tool_boids_network import ProperToolBoidsNetwork


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PROPER Tool Boids: Agents create real computational algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_proper_tools.py --agents 3 --steps 20
  python main_proper_tools.py --topology star --agents 4 --steps 30
  python main_proper_tools.py --quiet --export results.json
        """
    )
    
    parser.add_argument('--agents', type=int, default=3, choices=range(2, 11),
                       help='Number of agents (2-10, default: 3)')
    parser.add_argument('--steps', type=int, default=20,
                       help='Number of simulation steps (default: 20)')
    parser.add_argument('--topology', type=str, default='triangle',
                       choices=['triangle', 'line', 'star'],
                       help='Network topology (default: triangle)')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output (no step-by-step details)')
    parser.add_argument('--export', type=str, metavar='FILENAME',
                       help='Export results to JSON file')
    
    return parser.parse_args()


def print_banner():
    """Print startup banner."""
    print("""
🧮🤖 PROPER TOOL BOIDS - Real Computational Intelligence 🤖🧮

REAL ALGORITHMS CREATED:
• 🔢 MATH: Fibonacci, Prime checking, Factorials
• 📝 STRING: Palindrome detection, Word counting, Caesar cipher  
• 🧠 LOGIC: Boolean evaluation, Pattern recognition
• 📊 DATA: List sorting, Statistical analysis
• 🔐 CRYPTO: Hash functions, Encoding algorithms
• 📈 ANALYSIS: Sequence pattern detection

NO MORE FAKE TOOLS - EVERY FUNCTION IS REAL COMPUTATION!
""")


def print_simulation_setup(args):
    """Print simulation configuration."""
    print(f"📋 SIMULATION SETUP:")
    print(f"   👥 Agents: {args.agents}")
    print(f"   🔄 Steps: {args.steps}")  
    print(f"   🌐 Topology: {args.topology}")
    if args.export:
        print(f"   📁 Export to: {args.export}")


def main():
    """Main simulation orchestration."""
    args = parse_arguments()
    
    if not args.quiet:
        print_banner()
        print_simulation_setup(args)
        print()
    
    try:
        # Create network with proper tools
        network = ProperToolBoidsNetwork(
            num_agents=args.agents,
            topology=args.topology,
            azure_client=None,  # Using built-in algorithms
            reset_shared_tools=True
        )
        
        # Run simulation
        print("🚀 Starting PROPER computational tool creation...")
        results = network.run_simulation(
            num_steps=args.steps,
            verbose=not args.quiet
        )
        
        # Print summary
        if not args.quiet:
            print_final_summary(network)
        
        # Export results
        if args.export:
            network.export_results(args.export)
        else:
            # Auto-export with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_filename = f"proper_tools_{args.topology}_{args.agents}agents_{timestamp}.json"
            network.export_results(auto_filename)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return 1


def print_final_summary(network: ProperToolBoidsNetwork):
    """Print final simulation summary."""
    print("\n" + "="*70)
    print("📊 PROPER COMPUTATIONAL TOOLS SUMMARY")
    print("="*70)
    
    stats = network.get_summary_stats()
    
    print(f"🧮 Computational Tools Created: {stats['total_tools_created']}")
    print(f"🎭 Tool Type Diversity: {stats['tool_type_diversity']:.2f}")
    print(f"🎯 Agent Specialization: {stats['specialization_ratio']:.2f}")
    print(f"🤝 Collaboration Rate: {stats['collaboration_rate']:.2f}")
    print(f"📈 Overall Emergence Score: {stats['emergence_score']:.2f}")
    
    if stats['computational_domains']:
        print(f"🧠 Computational Domains: {', '.join(stats['computational_domains'])}")
    
    # Interpretation
    if stats['total_tools_created'] > 0:
        print("\n✨ SUCCESS: Real computational ecosystem emerged!")
        
        if stats['tool_type_diversity'] > 0.5:
            print("🌈 High diversity: Multiple computational domains explored")
            
        if stats['specialization_ratio'] > 0.5:
            print("🎯 Strong specialization: Agents developed different focuses")
            
        if stats['collaboration_rate'] > 0.3:
            print("🤝 Active collaboration: Agents used each other's algorithms")
            
        if stats['emergence_score'] > 0.5:
            print("🧬 High emergence: Complex computational behaviors from simple rules")
            
        print("\n🔍 VERIFICATION: Check personal_tools/ directories for real .py files")
        print("   Each file contains actual computational algorithms, not wrapper functions!")
        
    else:
        print("\n📝 No tools created - check system configuration")


def validate_environment():
    """Validate environment setup."""
    required_dirs = ['src']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"❌ Missing required directories: {missing_dirs}")
        print("Make sure you're running from the project root directory.")
        return False
    
    return True


if __name__ == "__main__":
    # Validate environment
    if not validate_environment():
        exit(1)
    
    # Run main simulation
    exit_code = main()
    exit(exit_code) 