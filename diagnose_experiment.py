#!/usr/bin/env python3
"""
Experiment Diagnoser for Emergent Intelligence Studies
=====================================================

This script provides post-hoc analysis and visualization for a completed
experiment run. It takes an experiment directory as input and generates
detailed plots of the Tool Complexity Index (TCI) evolution.

Usage:
    python diagnose_experiment.py --exp_dir experiments/exp1_baseline_emergence_...
"""

import os
import json
import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_experiment_data(results_file: str) -> dict:
    """Loads the main results.json file from an experiment."""
    if not os.path.exists(results_file):
        logger.error(f"Results file not found: {results_file}")
        return None
    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load or parse results file {results_file}: {e}")
        return None

def get_complexity_breakdown_over_rounds(results_data: dict) -> list:
    """
    Extracts the detailed, round-by-round complexity breakdown from the final
    tool metadata stored in the results file.
    """
    all_tools_metadata = {}
    # First, gather all tools and the round they were created in
    for round_data in results_data.get("round_results", []):
        for action in round_data.get("agent_actions", []):
            if action.get("tool_build_success"):
                # This is a simplification; we need the final complexity data.
                # The complexity_over_rounds from the runner is the source of truth.
                pass # This logic can be enhanced later if needed.

    # The ExperimentRunner already calculates the average TCI per round.
    # We need to recalculate the breakdown average here.
    round_by_round_breakdown = []
    
    # Get a list of all tools created by the end of the experiment
    final_tools = {}
    for round_data in results_data.get("round_results", []):
        # We need to find the final tool index state to get the complexity
        # This requires accessing the index.json files, which is complex here.
        # Let's assume the runner could store this breakdown.
        # For now, we will simulate this data for plotting purposes.
        # In a future refactor, ExperimentRunner should save this breakdown.
        
        # This is a placeholder. The real implementation will be more complex.
        # We will use the main TCI evolution plot for now and add this later.
        pass

    # For now, let's focus on plotting what run_experiment.py *does* save:
    # `complexity_over_rounds` which is in `results.json` under `final_statistics`.
    # Let's assume it was saved in the top level of results.json for now.
    
    # REVISED PLAN: We need to modify run_experiment.py to save this data first.
    # For now, this script will only plot the main TCI curve. The breakdown
    # requires a change in the data collection process.
    return results_data.get("complexity_over_rounds", [])

def get_complexity_of_new_tools_per_round(results_data: dict, exp_dir: str) -> list:
    """
    Calculates the average TCI of only the NEW tools created in each round.
    """
    # Load the final state of the shared tool index, which contains all complexity scores
    shared_index_file = os.path.join(exp_dir, "shared_tools", "index.json")
    if not os.path.exists(shared_index_file):
        logger.error(f"Cannot find final shared tool index at: {shared_index_file}")
        return []
    
    with open(shared_index_file, 'r') as f:
        final_tool_index = json.load(f).get("tools", {})

    tools_by_round = {}
    for round_data in results_data.get("round_results", []):
        round_num = round_data.get("round")
        if round_num is None:
            continue
        
        tools_by_round[round_num] = []
        for agent_action in round_data.get("agent_actions", []):
            if agent_action.get("tool_build_success"):
                # This part is tricky. The tool_info is not in the results.json
                # We need to find another way to get the tool name.
                # Let's check the promotion log messages. This is a hack for now.
                # A proper fix would be to save the tool name in agent_actions.
                pass 

    # We need a reliable way to know which tool was created each round.
    # The best source is the `created_at` timestamp in the index and round timestamps.
    # Let's try to map tools to rounds based on timestamps.

    round_timestamps = {r['round']: r['timestamp'] for r in results_data.get("round_results", [])}
    tools_created_in_round = {r: [] for r in round_timestamps.keys()}

    for tool_name, metadata in final_tool_index.items():
        created_at_str = metadata.get("created_at")
        if not created_at_str:
            continue
        
        # Find which round this tool belongs to
        best_round = -1
        for round_num, round_time_str in round_timestamps.items():
            if created_at_str >= round_time_str:
                best_round = round_num
        
        if best_round != -1:
            tools_created_in_round[best_round].append(tool_name)

    # Now calculate the average TCI for new tools in each round
    new_tools_tci_per_round = []
    for round_num, tool_names in tools_created_in_round.items():
        if not tool_names:
            avg_tci = 0
            # Carry over the last non-zero TCI to avoid a misleading drop to zero
            if new_tools_tci_per_round:
                avg_tci = new_tools_tci_per_round[-1]['average_tci_new_tools']
        else:
            total_tci = 0
            for tool_name in tool_names:
                total_tci += final_tool_index.get(tool_name, {}).get("complexity", {}).get("tci_score", 0)
            avg_tci = total_tci / len(tool_names)
        
        new_tools_tci_per_round.append({
            "round": round_num,
            "average_tci_new_tools": avg_tci,
            "new_tools_count": len(tool_names)
        })

    return new_tools_tci_per_round


def plot_overall_tci_evolution(exp_dir: str, complexity_data: list, new_tools_tci_data: list):
    """Plots both the overall average and the average of new tools."""
    if not complexity_data:
        logger.warning("No complexity data found to plot overall TCI evolution.")
        return

    df_overall = pd.DataFrame(complexity_data)
    df_new = pd.DataFrame(new_tools_tci_data)

    plt.figure(figsize=(12, 7))
    
    # Plot overall average TCI
    if 'average_tci' in df_overall.columns:
        plt.plot(df_overall['round'], df_overall['average_tci'], marker='o', linestyle='-', color='royalblue', label='Avg. TCI of ALL Tools (Ecosystem Health)')

    # Plot average TCI of NEW tools
    if 'average_tci_new_tools' in df_new.columns:
        plt.plot(df_new['round'], df_new['average_tci_new_tools'], marker='s', linestyle='--', color='firebrick', label='Avg. TCI of NEW Tools (Innovation Rate)')

    plt.title(f'Tool Complexity Evolution\n(Experiment: {os.path.basename(exp_dir)})', fontsize=16)
    plt.xlabel('Round Number', fontsize=12)
    plt.ylabel('Tool Complexity Index (TCI)', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    all_rounds = np.union1d(df_overall['round'], df_new['round'])
    plt.xticks(np.arange(min(all_rounds), max(all_rounds)+1, 1.0))
    
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(exp_dir, 'diagnostic_tci_evolution.png')
    plt.savefig(plot_path)
    logger.info(f"✅ Saved overall TCI evolution plot to: {plot_path}")
    plt.close()


def plot_tci_breakdown_evolution(exp_dir: str, complexity_breakdown_data: list):
    """
    Plots the breakdown of average TCI into its components as a stacked area chart.
    NOTE: This function depends on data that we will add to the experiment runner.
    """
    if not complexity_breakdown_data:
        logger.warning("No complexity breakdown data found. This requires a modification to run_experiment.py to save this data.")
        return

    df = pd.DataFrame(complexity_breakdown_data)
    required_cols = ['round', 'avg_code_complexity', 'avg_interface_complexity', 'avg_compositional_complexity']
    if not all(col in df.columns for col in required_cols):
        logger.error("Data for TCI breakdown plot is malformed or missing columns.")
        return

    # FIX: Apply the correct weights to each component for an accurate visualization
    # These weights must match those used in the ExperimentRunner.
    weights = {'alpha': 0.5, 'beta': 1.0, 'gamma': 10.0}
    
    weighted_code = df['avg_code_complexity'] * weights['alpha']
    weighted_interface = df['avg_interface_complexity'] * weights['beta']
    weighted_compositional = df['avg_compositional_complexity'] * weights['gamma']

    plt.figure(figsize=(12, 7))
    
    # We use a stacked area plot to show the components
    labels = [f"Code Complexity (x{weights['alpha']})", 
              f"Interface Complexity (x{weights['beta']})", 
              f"Compositional Complexity (x{weights['gamma']})"]
    colors = ['skyblue', 'salmon', 'lightgreen']
    
    plt.stackplot(df['round'],
                  weighted_code,
                  weighted_interface,
                  weighted_compositional,
                  labels=labels,
                  colors=colors,
                  alpha=0.8)

    plt.title(f'Weighted TCI Breakdown Evolution\n(Experiment: {os.path.basename(exp_dir)})', fontsize=16)
    plt.xlabel('Round Number', fontsize=12)
    plt.ylabel('Weighted Average TCI Component Score', fontsize=12)
    plt.xticks(np.arange(min(df['round']), max(df['round'])+1, 1.0))
    plt.legend(loc='upper left')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    plot_path = os.path.join(exp_dir, 'diagnostic_tci_breakdown.png')
    plt.savefig(plot_path)
    logger.info(f"✅ Saved TCI breakdown plot to: {plot_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Diagnose and visualize experiment results.")
    parser.add_argument("--exp_dir", required=True, help="Path to the experiment directory.")
    args = parser.parse_args()

    logger.info(f"🔬 Starting diagnosis for experiment: {args.exp_dir}")

    results_file = os.path.join(args.exp_dir, "results.json")
    results_data = load_experiment_data(results_file)

    if not results_data:
        return 1
    
    # --- Plotting ---
    complexity_data = results_data.get("complexity_over_rounds", [])
    new_tools_tci_data = get_complexity_of_new_tools_per_round(results_data, args.exp_dir)
    
    # Plot 1: Overall and New Tool TCI Evolution
    plot_overall_tci_evolution(args.exp_dir, complexity_data, new_tools_tci_data)

    # Plot 2: TCI Breakdown (will be enabled once data is available)
    plot_tci_breakdown_evolution(args.exp_dir, complexity_data)


if __name__ == "__main__":
    main() 