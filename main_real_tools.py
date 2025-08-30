#!/usr/bin/env python3
"""
Main entry point for Real Tool Boids simulation.

REAL TOOLS: Agents create, test, and use actual executable Python functions.
BOIDS RULES: Separation, alignment, cohesion guide tool creation decisions.
DRY PRINCIPLE: Reuses existing patterns while eliminating fake tool metadata.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Optional

from src.real_tool_boids_network import RealToolBoidsNetwork
# Azure client is optional
try:
    from src.azure_client import AzureOpenAIClient
except ImportError:
    AzureOpenAIClient = None


def parse_arguments():
    """Parse command line arguments. DRY: reuse argument patterns."""
    parser = argparse.ArgumentParser(
        description="Real Tool Boids: Agents create and evolve actual executable tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_real_tools.py --agents 3 --steps 30
  python main_real_tools.py --topology star --agents 5 --steps 50 --llm
  python main_real_tools.py --quiet --export results.json
        """
    )
    
    # Core simulation parameters (DRY: common parameters)
    parser.add_argument('--agents', type=int, default=3, choices=range(2, 11),
                       help='Number of agents (2-10, default: 3)')
    parser.add_argument('--steps', type=int, default=50,
                       help='Number of simulation steps (default: 50)')
    parser.add_argument('--topology', type=str, default='triangle',
                       choices=['triangle', 'line', 'star'],
                       help='Network topology (default: triangle)')
    
    # Tool creation options
    parser.add_argument('--llm', action='store_true',
                       help='Use LLM for tool creation (requires Azure OpenAI setup)')
    parser.add_argument('--reset-shared', action='store_true', default=True,
                       help='Reset shared tools to template (default: True)')
    
    # Output options (DRY: common output patterns)
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output (no step-by-step details)')
    parser.add_argument('--export', type=str, metavar='FILENAME',
                       help='Export results to JSON file')
    
    return parser.parse_args()


def setup_azure_client():
    """Setup Azure OpenAI client if available. DRY: optional setup pattern."""
    if AzureOpenAIClient is None:
        print("⚠️  Azure OpenAI not available. Using templates for tool creation.")
        return None
        
    try:
        # Check for Azure credentials
        if not all([
            os.getenv('AZURE_OPENAI_ENDPOINT'),
            os.getenv('AZURE_OPENAI_API_KEY'),
            os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        ]):
            print("⚠️  Azure OpenAI credentials not found. Using templates for tool creation.")
            return None
        
        return AzureOpenAIClient()
        
    except Exception as e:
        print(f"⚠️  Could not setup Azure client: {e}. Using templates for tool creation.")
        return None


def print_banner():
    """Print startup banner. DRY: consistent branding."""
    print("""
🔧🤖 REAL TOOL BOIDS - Emergent Tool Creation & Evolution 🤖🔧

Key Features:
• 🎯 REAL TOOLS: Agents create actual executable Python functions
• 🐦 BOIDS RULES: Separation, alignment, cohesion guide decisions  
• 🧪 TESTING: Generated test cases validate tool functionality
• 📈 EVOLUTION: Successful tools graduate to shared pool
• 🤝 COLLABORATION: Agents use and improve each other's tools

Rules Explained:
🔸 SEPARATION: Avoid creating tools similar to what neighbors just made
🔸 ALIGNMENT: Copy strategies of neighbors who have more tools (success)
🔸 COHESION: Use and build upon neighbors' existing tools
""")


def print_simulation_setup(args, azure_client):
    """Print simulation configuration. DRY: setup summary."""
    print(f"📋 SIMULATION SETUP:")
    print(f"   👥 Agents: {args.agents}")
    print(f"   🔄 Steps: {args.steps}")  
    print(f"   🌐 Topology: {args.topology}")
    print(f"   🧠 LLM Tool Creation: {'Yes' if azure_client else 'No (Templates)'}")
    print(f"   🔄 Reset Shared Tools: {'Yes' if args.reset_shared else 'No'}")
    if args.export:
        print(f"   📁 Export to: {args.export}")


def main():
    """Main simulation orchestration. DRY: main pattern."""
    args = parse_arguments()
    
    if not args.quiet:
        print_banner()
        
    # Setup LLM client (DRY: optional dependency)
    azure_client = setup_azure_client() if args.llm else None
    
    if not args.quiet:
        print_simulation_setup(args, azure_client)
        print()
    
    try:
        # Create network (DRY: network initialization)
        network = RealToolBoidsNetwork(
            num_agents=args.agents,
            topology=args.topology,
            azure_client=azure_client,
            reset_shared_tools=args.reset_shared
        )
        
        # Run simulation (DRY: simulation execution)
        print("🚀 Starting simulation...")
        results = network.run_simulation(
            num_steps=args.steps,
            verbose=not args.quiet
        )
        
        # Print summary (DRY: result summary)
        if not args.quiet:
            print_final_summary(network)
        
        # Export results (DRY: export pattern)
        if args.export:
            network.export_results(args.export)
        else:
            # Auto-export with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_filename = f"real_tools_{args.topology}_{args.agents}agents_{timestamp}.json"
            network.export_results(auto_filename)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return 1


def print_final_summary(network: RealToolBoidsNetwork):
    """Print final simulation summary. DRY: summary formatting."""
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    # Get summary statistics (DRY: reuse network stats)
    stats = network.get_summary_stats()
    
    print(f"🔧 Tools Created: {stats['total_tools_created']}")
    print(f"🎯 Specialization: {stats['specialization_ratio']:.2f}")
    print(f"🤝 Collaboration Rate: {stats['collaboration_rate']:.2f}")
    print(f"📈 Emergence Score: {stats['emergence_score']:.2f}")
    
    # Interpretation (DRY: evaluation criteria)
    if stats['total_tools_created'] > 0:
        print("\n✨ SUCCESS: Real tool ecosystem emerged!")
        
        if stats['specialization_ratio'] > 0.5:
            print("🎯 Strong specialization: Agents developed different roles")
            
        if stats['collaboration_rate'] > 0.3:
            print("🤝 Active collaboration: Agents frequently used each other's tools")
            
        if stats['emergence_score'] > 0.5:
            print("🧬 High emergence: Complex behaviors from simple rules")
    else:
        print("\n📝 No tools created. Check:")
        print("   • Agent configuration")
        print("   • Tool creation templates")
        print("   • Simulation parameters")
    
    print(f"\n🔍 Check personal_tools/ directories for created tool files")


def validate_environment():
    """Validate environment setup. DRY: validation pattern."""
    required_dirs = ['src', 'shared_tools']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"❌ Missing required directories: {missing_dirs}")
        print("Make sure you're running from the project root directory.")
        return False
    
    return True


if __name__ == "__main__":
    # Validate environment (DRY: startup validation)
    if not validate_environment():
        exit(1)
    
    # Run main simulation
    exit_code = main()
    exit(exit_code) 