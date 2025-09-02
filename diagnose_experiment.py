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


def plot_overall_tci_evolution(exp_dir: str, complexity_data: list):
    """Plots the primary 'Average TCI vs. Round Number' curve."""
    if not complexity_data:
        logger.warning("No complexity data found to plot overall TCI evolution.")
        return

    df = pd.DataFrame(complexity_data)
    if 'round' not in df.columns or 'average_tci' not in df.columns:
        logger.error("Data for overall TCI plot is malformed.")
        return

    plt.figure(figsize=(12, 7))
    plt.plot(df['round'], df['average_tci'], marker='o', linestyle='-', color='royalblue', label='Average TCI')
    plt.title(f'Overall Tool Complexity Evolution\n(Experiment: {os.path.basename(exp_dir)})', fontsize=16)
    plt.xlabel('Round Number', fontsize=12)
    plt.ylabel('Average Tool Complexity Index (TCI)', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(np.arange(min(df['round']), max(df['round'])+1, 1.0))
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

    plt.figure(figsize=(12, 7))
    
    # We use a stacked area plot to show the components
    labels = ['Code Complexity', 'Interface Complexity', 'Compositional Complexity']
    colors = ['skyblue', 'salmon', 'lightgreen']
    
    plt.stackplot(df['round'],
                  df['avg_code_complexity'],
                  df['avg_interface_complexity'],
                  df['avg_compositional_complexity'],
                  labels=labels,
                  colors=colors,
                  alpha=0.8)

    plt.title(f'TCI Breakdown Evolution\n(Experiment: {os.path.basename(exp_dir)})', fontsize=16)
    plt.xlabel('Round Number', fontsize=12)
    plt.ylabel('Average TCI Component Score', fontsize=12)
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
    # NOTE: As designed, we first need to modify the runner to save the breakdown.
    # The complexity_over_rounds in the results file needs to be enhanced.
    # For now, only the first plot will work if the data is present.
    
    complexity_data = results_data.get("complexity_over_rounds", [])
    
    # Plot 1: Overall TCI Evolution
    plot_overall_tci_evolution(args.exp_dir, complexity_data)

    # Plot 2: TCI Breakdown (will be enabled once data is available)
    plot_tci_breakdown_evolution(args.exp_dir, complexity_data)


if __name__ == "__main__":
    main() 