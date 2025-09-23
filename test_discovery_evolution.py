#!/usr/bin/env python3
"""
Test script for Dynamic Specialization Discovery Evolution
Demonstrates the enhanced evolutionary algorithm with behavioral analysis
"""

import os
import sys
sys.path.append('.')

from run_experiment import ExperimentRunner


def test_discovery_evolution():
    """Test evolution with dynamic specialization discovery"""
    print("🧬 Testing Discovery-Enhanced Evolution")
    print("=" * 60)
    
    # Test configuration for discovery evolution
    experiment_name = "discovery_evolution_test"
    num_agents = 4
    max_rounds = 7  # Enough rounds to see multiple evolutions
    evolution_frequency = 3  # Evolve every 3 rounds
    
    # Define initial specializations (these will be refined through discovery)
    initial_specializations = [
        "Focus on data processing and transformation tools",
        "Build mathematical computation and analysis tools", 
        "Create file management and organization utilities",
        "Develop text processing and string manipulation tools"
    ]
    
    # Base meta-prompt for collaboration
    shared_meta_prompt = """You are collaborating with other AI agents to build a comprehensive toolkit. 
Your goal is to create practical, well-tested tools that complement each other and serve diverse use cases.
Focus on building tools that can be composed together to solve complex problems."""
    
    print(f"🔧 Configuration:")
    print(f"   Agents: {num_agents}")
    print(f"   Rounds: {max_rounds}")
    print(f"   Evolution frequency: {evolution_frequency}")
    print(f"   Discovery-enhanced evolution: ENABLED")
    print(f"   Boids coordination: ENABLED")
    
    try:
        # Create experiment runner with discovery evolution
        runner = ExperimentRunner(
            experiment_name=experiment_name,
            num_agents=num_agents,
            max_rounds=max_rounds,
            shared_meta_prompt=shared_meta_prompt,
            agent_specializations=initial_specializations,
            boids_enabled=True,
            boids_k_neighbors=2,
            boids_sep_threshold=0.45,
            evolution_enabled=True,  # 🧬 Enable evolution
            evolution_frequency=evolution_frequency,
            evolution_selection_rate=0.25  # Remove 25% (1 agent)
        )
        
        print(f"\n🚀 Starting Discovery Evolution Experiment...")
        print(f"   Expected evolution at rounds: {[r for r in range(evolution_frequency, max_rounds, evolution_frequency)]}")
        
        # Run the experiment
        results = runner.run_experiment()
        
        # Display results
        print(f"\n📊 Discovery Evolution Results:")
        print("=" * 60)
        
        print(f"✅ Experiment completed successfully!")
        print(f"   Total rounds: {results['total_rounds']}")
        print(f"   Final agents: {results['final_num_agents']}")
        print(f"   Boids enabled: {results['boids_enabled']}")
        print(f"   Evolution enabled: {results['evolution_enabled']}")
        
        # Evolution summary
        if results.get('evolution_summary'):
            evo_summary = results['evolution_summary']
            print(f"\n🧬 Evolution Summary:")
            print(f"   Generations: {evo_summary.get('generations', 0)}")
            print(f"   Total agents eliminated: {evo_summary.get('total_agents_eliminated', 0)}")
            print(f"   Total agents created: {evo_summary.get('total_agents_created', 0)}")
            print(f"   Latest avg complexity: {evo_summary.get('latest_avg_complexity', 0):.2f}")
            print(f"   Complexity improvement: {evo_summary.get('complexity_improvement', 0):.2f}")
        
        # Final agent details
        print(f"\n👥 Final Agent Population:")
        final_agents = results.get('final_agents', [])
        for agent_data in final_agents:
            agent_id = agent_data['agent_id']
            specialization = agent_data.get('specific_prompt', 'No specialization')
            tools_count = agent_data.get('tools_built', 0)
            print(f"   {agent_id}: {tools_count} tools")
            print(f"      Specialization: {specialization[:80]}...")
        
        # Performance metrics
        print(f"\n📈 Performance Metrics:")
        print(f"   Total tools created: {results.get('total_tools_created', 0)}")
        print(f"   Total tests created: {results.get('total_tests_created', 0)}")
        print(f"   Avg tools per agent: {results.get('avg_tools_per_agent', 0):.1f}")
        print(f"   Experiment duration: {results.get('duration_seconds', 0):.1f}s")
        
        # Show key discovery insights
        if 'round_results' in results:
            print(f"\n🔍 Discovery Evolution Insights:")
            evolution_rounds = [r for r in results['round_results'] if 'evolution_occurred' in r]
            for i, round_data in enumerate(evolution_rounds):
                round_num = round_data.get('round_number', i+1)
                print(f"   Round {round_num}: Specializations updated and evolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Discovery evolution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    success = test_discovery_evolution()
    
    if success:
        print(f"\n🎉 Discovery Evolution Test Completed Successfully!")
        print(f"🧬 Agents now evolve with behavioral analysis and specialization discovery")
        print(f"🎯 Each evolution cycle refines agents based on what they actually do")
    else:
        print(f"\n❌ Discovery Evolution Test Failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
