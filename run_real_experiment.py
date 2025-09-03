#!/usr/bin/env python3
"""
Real Experiment Runner for Emergent Intelligence Studies
=========================================================

This script orchestrates the execution of formal experiments based on a set of
pre-defined meta-prompts. It handles experiment setup, execution, and result
analysis, including the plotting of Tool Complexity Index (TCI) evolution.

Experiment 1: "Baseline Emergence"
- Agents start with no specializations.
- All guidance comes from a single, shared meta-prompt.
- The system observes how agents specialize and develop tools in response
  to the high-level objective without explicit instructions.

Usage:
    python run_real_experiment.py --meta_prompt_id "data_science_suite" --num_agents 3 --num_rounds 10
"""

import os
import json
import argparse
import logging
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

from run_experiment import ExperimentRunner
from src.complexity_analyzer import TCIAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_experiment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_meta_prompts(file_path: str = 'meta_prompts.json') -> Dict[str, str]:
    """Loads the meta-prompts from the JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return {prompt['id']: prompt['description'] for prompt in data['meta_prompts']}
    except FileNotFoundError:
        logger.error(f"Meta prompts file not found at: {file_path}")
        return {}
    except (KeyError, json.JSONDecodeError):
        logger.error(f"Invalid format in meta prompts file: {file_path}")
        return {}


def plot_complexity_evolution(experiment_dir: str, complexity_data: List[Dict[str, Any]]):
    """
    Analyzes the experiment results to plot the evolution of tool complexity.
    """
    if not complexity_data:
        logger.warning("No complexity data provided to plot.")
        return

    logger.info("📊 Plotting Tool Complexity Evolution...")
    
    try:
        df = pd.DataFrame(complexity_data)
        
        if 'round' not in df.columns or 'average_tci' not in df.columns:
            logger.error("Complexity data is missing 'round' or 'average_tci' columns.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(df['round'], df['average_tci'], marker='o', linestyle='-', color='b')
        
        plt.xlabel('Round Number')
        plt.ylabel('Average Tool Complexity Index (TCI)')
        plt.title('Evolution of Average Tool Complexity Over Time')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xticks(df['round']) # Ensure integer round numbers on x-axis
        
        # Set y-axis to start from 0
        plt.ylim(bottom=0)

        plot_path = os.path.join(experiment_dir, 'tci_evolution_plot.png')
        plt.savefig(plot_path)
        logger.info(f"📈 Complexity evolution plot saved to: {plot_path}")
        plt.close()
        
    except Exception as e:
        logger.error(f"Failed to plot complexity evolution: {e}")


def run_single_experiment(exp_name: str, meta_prompt: str, num_agents: int, num_rounds: int, boids_enabled: bool, boids_k: int, boids_sep: float):
    """
    Configures and runs a single experiment.
    """
    logger.info("=" * 70)
    logger.info(f"🚀 Launching Experiment: {exp_name}")
    logger.info(f"🎯 Meta-Prompt: {meta_prompt[:100]}...")
    logger.info(f"👥 Agents: {num_agents}, 🔄 Rounds: {num_rounds}")
    logger.info(f"🐦 Boids Enabled: {boids_enabled} (k={boids_k}, sep={boids_sep})")
    logger.info("=" * 70)
    
    # In this experiment, agents have no specific specializations
    agent_specializations = [""] * num_agents
    
    runner = ExperimentRunner(
        experiment_name=exp_name,
        num_agents=num_agents,
        max_rounds=num_rounds,
        shared_meta_prompt=meta_prompt,
        agent_specializations=agent_specializations,
        boids_enabled=boids_enabled,
        boids_k_neighbors=boids_k,
        boids_sep_threshold=boids_sep
    )
    
    success = runner.run_experiment()
    
    if success:
        logger.info("✅ Experiment run completed successfully.")
        # Plot complexity at the end using the tracked data
        # plot_complexity_evolution(runner.experiment_dir, runner.complexity_over_rounds)
    else:
        logger.error("❌ Experiment run failed.")
    
    logger.info("=" * 70)
    logger.info(f"🎉 Experiment Finished: {exp_name}")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Run Formal Emergent Intelligence Experiments")
    parser.add_argument("--meta_prompt_id", required=True, help="The ID of the meta-prompt to use from meta_prompts.json")
    parser.add_argument("--num_agents", type=int, default=3, help="Number of agents in the society.")
    parser.add_argument("--num_rounds", type=int, default=10, help="Number of simulation rounds.")
    parser.add_argument("--boids_enabled", action='store_true', help="Enable Boids rules for agent behavior.")
    parser.add_argument("--boids_k", type=int, default=2, help="Number of neighbors for Boids rules (k).")
    parser.add_argument("--boids_sep", type=float, default=0.45, help="Separation threshold for Boids rules.")
    
    args = parser.parse_args()
    
    # Load meta-prompts
    meta_prompts = load_meta_prompts()
    if not meta_prompts:
        return 1
    
    selected_prompt = meta_prompts.get(args.meta_prompt_id)
    if not selected_prompt:
        logger.error(f"Meta-prompt ID '{args.meta_prompt_id}' not found in meta_prompts.json.")
        logger.info(f"Available IDs: {list(meta_prompts.keys())}")
        return 1
        
    # Define the experiment name
    mode = "boids" if args.boids_enabled else "global"
    exp_name = f"exp_{mode}_{args.meta_prompt_id}"
    
    # Run the experiment
    run_single_experiment(
        exp_name=exp_name,
        meta_prompt=selected_prompt,
        num_agents=args.num_agents,
        num_rounds=args.num_rounds,
        boids_enabled=args.boids_enabled,
        boids_k=args.boids_k,
        boids_sep=args.boids_sep
    )
    
    return 0


if __name__ == "__main__":
    exit(main()) 