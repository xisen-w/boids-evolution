#!/usr/bin/env python3
"""
Test script for Evolutionary Algorithm integration
Demonstrates how to run experiments with evolution enabled.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from run_experiment import ExperimentRunner


def test_evolutionary_experiment():
    """Test the evolutionary algorithm with a small experiment."""
    
    print("🧬 Testing Evolutionary Algorithm Integration")
    print("=" * 60)
    
    # Define agent specializations
    specializations = [
        "Focus on building MATHEMATICAL and CALCULATION tools. Create tools for numerical operations.",
        "Focus on building TEXT PROCESSING and STRING manipulation tools. Create tools for text analysis.",
        "Focus on building DATA PROCESSING tools. Create tools for data transformation and analysis.",
        "Focus on building FILE SYSTEM tools. Create tools for file operations and management.",
        "Focus on building UTILITY tools. Create tools for general purpose operations."
    ]
    
    # Create experiment runner with evolution enabled
    runner = ExperimentRunner(
        experiment_name="evolutionary_test",
        num_agents=5,  # Start with 5 agents
        max_rounds=5,  # Run for 5 rounds
        shared_meta_prompt="You are in a collaborative tool-building ecosystem. Create high-quality, complex tools that solve real problems.",
        agent_specializations=specializations,
        boids_enabled=True,
        boids_k_neighbors=2,
        boids_sep_threshold=0.45,
        evolution_enabled=True,      # Enable evolution
        evolution_frequency=3,       # Evolve at round 3
        evolution_selection_rate=0.2 # Remove bottom 20% (1 agent out of 5)
    )
    
    print(f"🔬 Experiment Configuration:")
    print(f"   Agents: {runner.num_agents}")
    print(f"   Rounds: {runner.max_rounds}")
    print(f"   Boids: {'Enabled' if runner.boids_enabled else 'Disabled'}")
    print(f"   Evolution: {'Enabled' if runner.evolution_enabled else 'Disabled'}")
    if runner.evolution_enabled:
        print(f"   Evolution frequency: Every {runner.evolution_frequency} rounds")
        print(f"   Selection rate: {runner.evolution_selection_rate * 100}%")
    print()
    
    # Run the experiment
    success = runner.run_experiment()
    
    if success:
        print(f"\n✅ Evolutionary experiment completed successfully!")
        print(f"📁 Results saved in: {runner.experiment_dir}")
        
        # Show evolution statistics if available
        if runner.evolution_enabled and runner.evolutionary_algorithm:
            evolution_summary = runner.evolutionary_algorithm.get_evolution_summary()
            if evolution_summary.get("generations", 0) > 0:
                print(f"\n🧬 Final Evolution Statistics:")
                print(f"   Generations completed: {evolution_summary['generations']}")
                print(f"   Complexity improvement: {evolution_summary['complexity_improvement']:.2f}")
                print(f"   Agents eliminated: {evolution_summary['total_agents_eliminated']}")
                print(f"   Agents created: {evolution_summary['total_agents_created']}")
    else:
        print(f"\n❌ Evolutionary experiment failed!")
    
    return success


def test_no_evolution_experiment():
    """Test the same experiment without evolution for comparison."""
    
    print("\n🔬 Testing Control Experiment (No Evolution)")
    print("=" * 60)
    
    # Define agent specializations (same as evolutionary test)
    specializations = [
        "Focus on building MATHEMATICAL and CALCULATION tools. Create tools for numerical operations.",
        "Focus on building TEXT PROCESSING and STRING manipulation tools. Create tools for text analysis.",
        "Focus on building DATA PROCESSING tools. Create tools for data transformation and analysis.",
        "Focus on building FILE SYSTEM tools. Create tools for file operations and management.",
        "Focus on building UTILITY tools. Create tools for general purpose operations."
    ]
    
    # Create experiment runner WITHOUT evolution
    runner = ExperimentRunner(
        experiment_name="control_test",
        num_agents=5,
        max_rounds=5,
        shared_meta_prompt="You are in a collaborative tool-building ecosystem. Create high-quality, complex tools that solve real problems.",
        agent_specializations=specializations,
        boids_enabled=True,
        boids_k_neighbors=2,
        boids_sep_threshold=0.45,
        evolution_enabled=False  # Evolution disabled
    )
    
    print(f"🔬 Control Experiment Configuration:")
    print(f"   Agents: {runner.num_agents}")
    print(f"   Rounds: {runner.max_rounds}")
    print(f"   Boids: {'Enabled' if runner.boids_enabled else 'Disabled'}")
    print(f"   Evolution: {'Enabled' if runner.evolution_enabled else 'Disabled'}")
    print()
    
    # Run the control experiment
    success = runner.run_experiment()
    
    if success:
        print(f"\n✅ Control experiment completed successfully!")
        print(f"📁 Results saved in: {runner.experiment_dir}")
    else:
        print(f"\n❌ Control experiment failed!")
    
    return success


if __name__ == "__main__":
    print("🧪 Evolutionary Algorithm Testing Suite")
    print("=" * 70)
    
    # Test with evolution enabled
    evo_success = test_evolutionary_experiment()
    
    # Test without evolution for comparison
    control_success = test_no_evolution_experiment()
    
    print("\n" + "=" * 70)
    print("📊 Testing Summary:")
    print(f"   Evolutionary experiment: {'✅ Success' if evo_success else '❌ Failed'}")
    print(f"   Control experiment: {'✅ Success' if control_success else '❌ Failed'}")
    
    if evo_success and control_success:
        print("\n🎉 All tests completed successfully!")
        print("💡 Compare the results in the experiment directories to see the impact of evolution.")
    else:
        print("\n⚠️  Some tests failed. Check the logs for details.") 