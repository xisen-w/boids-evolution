#!/usr/bin/env python3
"""
Complexity Visualization Guide
==============================

This script demonstrates how to use the complexity visualization tools
in the boids-evolution project.

There are 3 main ways to visualize complexity:

1. Built-in TCI evolution plot (simple line chart)
2. Advanced demo visualizer (animated boids + complexity)  
3. Interactive dashboard (web-based)
"""

import os
import json
import argparse
from pathlib import Path

# Import our visualization modules
from visualizations.demo_visualizer import BoidsEvolutionVisualizer
from run_real_experiment import plot_complexity_evolution


def demonstrate_simple_tci_plot(experiment_dir: str):
    """
    Method 1: Simple TCI Evolution Plot
    ==================================
    
    Uses the built-in function from run_real_experiment.py
    Creates a basic line chart showing TCI over rounds.
    """
    print("\n🔹 Method 1: Simple TCI Evolution Plot")
    print("=" * 50)
    
    # Load experiment data to extract complexity evolution
    results_file = Path(experiment_dir) / 'results.json'
    if not results_file.exists():
        print(f"❌ No results.json found in {experiment_dir}")
        return
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Extract complexity data from results
    complexity_data = data.get('complexity_over_rounds', [])
    
    if not complexity_data:
        print("⚠️  No complexity_over_rounds data found in results.json")
        print("   This data is typically generated during experiment runs")
        return
    
    # Use the built-in plotting function
    plot_complexity_evolution(experiment_dir, complexity_data)
    print(f"✅ TCI evolution plot saved to: {experiment_dir}/tci_evolution_plot.png")


def demonstrate_advanced_visualizer(experiment_dir: str):
    """
    Method 2: Advanced Demo Visualizer
    ==================================
    
    Uses the BoidsEvolutionVisualizer class for rich animations
    and complexity breakdowns.
    """
    print("\n🔹 Method 2: Advanced Demo Visualizer")  
    print("=" * 50)
    
    try:
        # Initialize the visualizer
        visualizer = BoidsEvolutionVisualizer(experiment_dir)
        
        # Create animated evolution (saves as .gif)
        print("📹 Creating animated evolution visualization...")
        visualizer.create_evolution_animation(
            output_file=f"{experiment_dir}/boids_evolution_animation.gif",
            duration=200,  # milliseconds per frame
            show_stats=True
        )
        print(f"✅ Animation saved to: {experiment_dir}/boids_evolution_animation.gif")
        
        # Create interactive dashboard
        print("🌐 Creating interactive dashboard...")
        visualizer.create_interactive_dashboard(
            output_file=f"{experiment_dir}/evolution_dashboard.html"
        )
        print(f"✅ Dashboard saved to: {experiment_dir}/evolution_dashboard.html")
        
        # Create summary report
        print("📊 Creating summary report...")
        visualizer.create_summary_report(
            output_file=f"{experiment_dir}/evolution_summary_report.html"
        )
        print(f"✅ Summary report saved to: {experiment_dir}/evolution_summary_report.html")
        
    except Exception as e:
        print(f"❌ Error creating advanced visualizations: {e}")


def demonstrate_manual_complexity_analysis(experiment_dir: str):
    """
    Method 3: Manual Complexity Analysis
    ====================================
    
    Shows how to manually analyze TCI data from the experiment.
    """
    print("\n🔹 Method 3: Manual Complexity Analysis")
    print("=" * 50)
    
    # Load TCI metrics
    tci_file = Path(experiment_dir) / 'tci_metrics.json'
    if not tci_file.exists():
        print(f"❌ No tci_metrics.json found in {experiment_dir}")
        return
    
    with open(tci_file, 'r') as f:
        tci_data = json.load(f)
    
    print("📈 TCI Analysis Summary:")
    print("-" * 30)
    
    all_tools = []
    for agent_id, tools in tci_data.items():
        for tool_name, metrics in tools.items():
            if isinstance(metrics, dict) and 'tci_score' in metrics:
                all_tools.append({
                    'agent': agent_id,
                    'tool': tool_name,
                    'tci_score': metrics['tci_score'],
                    'code_complexity': metrics.get('code_complexity', 0),
                    'interface_complexity': metrics.get('interface_complexity', 0),
                    'compositional_complexity': metrics.get('compositional_complexity', 0),
                    'lines_of_code': metrics.get('lines_of_code', 0),
                })
    
    if not all_tools:
        print("❌ No valid TCI data found")
        return
    
    # Calculate statistics
    tci_scores = [t['tci_score'] for t in all_tools]
    code_scores = [t['code_complexity'] for t in all_tools]
    interface_scores = [t['interface_complexity'] for t in all_tools]
    comp_scores = [t['compositional_complexity'] for t in all_tools]
    
    print(f"🔢 Total Tools Analyzed: {len(all_tools)}")
    print(f"📊 Average TCI Score: {sum(tci_scores)/len(tci_scores):.2f}")
    print(f"📈 TCI Range: {min(tci_scores):.2f} - {max(tci_scores):.2f}")
    print(f"⚙️  Code Complexity Avg: {sum(code_scores)/len(code_scores):.2f}")
    print(f"🔌 Interface Complexity Avg: {sum(interface_scores)/len(interface_scores):.2f}")
    print(f"🔗 Compositional Complexity Avg: {sum(comp_scores)/len(comp_scores):.2f}")
    
    # Show top 5 most complex tools
    sorted_tools = sorted(all_tools, key=lambda x: x['tci_score'], reverse=True)
    print(f"\n🏆 Top 5 Most Complex Tools:")
    for i, tool in enumerate(sorted_tools[:5], 1):
        print(f"  {i}. {tool['agent']}/{tool['tool']} - TCI: {tool['tci_score']:.2f}")


def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description="Complexity Visualization Guide")
    parser.add_argument("experiment_dir", help="Path to experiment directory")
    parser.add_argument("--method", choices=['simple', 'advanced', 'manual', 'all'], 
                       default='all', help="Which visualization method to demonstrate")
    
    args = parser.parse_args()
    
    if not Path(args.experiment_dir).exists():
        print(f"❌ Experiment directory not found: {args.experiment_dir}")
        return 1
    
    print(f"🧪 Analyzing experiment: {args.experiment_dir}")
    print("=" * 60)
    
    if args.method in ['simple', 'all']:
        demonstrate_simple_tci_plot(args.experiment_dir)
    
    if args.method in ['advanced', 'all']:
        demonstrate_advanced_visualizer(args.experiment_dir)
    
    if args.method in ['manual', 'all']:
        demonstrate_manual_complexity_analysis(args.experiment_dir)
    
    print("\n🎉 Complexity visualization demonstration complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
