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


def load_meta_prompts(file_path: str = 'meta_prompts_enhanced_v2.json') -> Dict[str, str]:
    """Loads the enhanced meta-prompts from the JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return {prompt['id']: f"{prompt['description']} \n Open Question: {prompt['open_question']}" for prompt in data['meta_prompts']}
    except FileNotFoundError:
        logger.error(f"Enhanced meta prompts file not found at: {file_path}")
        # Fallback to original meta_prompts.json
        try:
            with open('meta_prompts.json', 'r') as f:
                data = json.load(f)
            logger.info("Using fallback meta_prompts.json")
            return {prompt['id']: prompt['description'] for prompt in data['meta_prompts']}
        except:
            logger.error("Both enhanced and original meta prompts files failed to load")
            return {}
    except (KeyError, json.JSONDecodeError):
        logger.error(f"Invalid format in meta prompts file: {file_path}")
        return {}


def verify_resources() -> bool:
    """Verify that required resource files are accessible."""
    logger.info("🔍 Verifying resource files...")
    
    required_resources = [
        "resources/task_1_crocodile_dataset.csv",
        "resources/task_2_insurance.csv", 
        "resources/task_3_GDP.csv",
        "resources/task_4_bi.csv",
        "resources/task_5_creditcard.csv",
        "resources/task_6_maths_notes.pdf",
        "resources/task_7_journey_to_the_west.pdf",
        "resources/task_8_sonnets_18.pdf",
        "resources/task_9_grid_runner_PRD.pdf",
        "resources/task_10_to_do_lite_PRD.pdf"
    ]
    
    missing_resources = []
    for resource in required_resources:
        if not os.path.exists(resource):
            missing_resources.append(resource)
        else:
            # Check file size to ensure it's not empty
            size = os.path.getsize(resource)
            logger.info(f"   ✅ {resource} ({size:,} bytes)")
    
    if missing_resources:
        logger.error("❌ Missing resources:")
        for resource in missing_resources:
            logger.error(f"   - {resource}")
        return False
    
    logger.info("✅ All resources verified successfully!")
    return True


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


def run_single_experiment(exp_name: str, meta_prompt: str, num_agents: int, num_rounds: int, 
                         boids_enabled: bool, boids_k: int, boids_sep: float, 
                         boids_separation_enabled: bool = True,
                         boids_alignment_enabled: bool = True, 
                         boids_cohesion_enabled: bool = True,
                         evolution_enabled: bool = False,
                         evolution_frequency: int = 5,
                         evolution_selection_rate: float = 0.2,
                         self_reflection: bool = False,
                         model_name: str = "default"):
    """
    Configures and runs a single experiment with full ablation support.
    """
    logger.info("=" * 70)
    logger.info(f"🚀 Launching Experiment: {exp_name}")
    logger.info(f"🎯 Meta-Prompt: {meta_prompt[:100]}...")
    logger.info(f"👥 Agents: {num_agents}, 🔄 Rounds: {num_rounds}")
    logger.info(f"🤖 Model: {model_name}")
    logger.info(f"🐦 Boids Enabled: {boids_enabled} (k={boids_k}, sep={boids_sep})")
    if boids_enabled:
        logger.info(f"   ├─ Separation: {boids_separation_enabled}")
        logger.info(f"   ├─ Alignment: {boids_alignment_enabled}")
        logger.info(f"   └─ Cohesion: {boids_cohesion_enabled}")
    logger.info(f"🧬 Evolution: {evolution_enabled} (freq={evolution_frequency}, rate={evolution_selection_rate})")
    logger.info(f"🤔 Self-Reflection: {self_reflection}")
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
        boids_sep_threshold=boids_sep,
        # NEW: Individual rule controls
        boids_separation_enabled=boids_separation_enabled,
        boids_alignment_enabled=boids_alignment_enabled,
        boids_cohesion_enabled=boids_cohesion_enabled,
        # NEW: Evolution controls
        evolution_enabled=evolution_enabled,
        evolution_frequency=evolution_frequency,
        evolution_selection_rate=evolution_selection_rate,
        self_reflection_enabled=self_reflection,
        model_name=model_name
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


def run_ablation_study(meta_prompt: str, num_agents: int, num_rounds: int, 
                      boids_k: int = 2, boids_sep: float = 0.45, 
                      evolution_frequency: int = 5, evolution_selection_rate: float = 0.2,
                      model_name: str = "default"):
    """
    Runs a complete ablation study with all 6 experiment configurations.
    """
    logger.info("🧪 Starting Complete Ablation Study")
    logger.info("=" * 70)
    
    experiments = [
        # 1. Single Loop (baseline)
        {
            "name": "single_loop",
            "boids_enabled": False,
            "boids_separation_enabled": False,
            "boids_alignment_enabled": False,
            "boids_cohesion_enabled": False,
            "evolution_enabled": False,
            "self_reflection": False
        },
        # 2. Single Loop + Boids - R1 (Separation only)
        {
            "name": "single_loop_boids_r1_separation",
            "boids_enabled": True,
            "boids_separation_enabled": True,
            "boids_alignment_enabled": False,
            "boids_cohesion_enabled": False,
            "evolution_enabled": False,
            "self_reflection": False
        },
        # 3. Single Loop + Boids - R2 (Alignment only)
        {
            "name": "single_loop_boids_r2_alignment",
            "boids_enabled": True,
            "boids_separation_enabled": False,
            "boids_alignment_enabled": True,
            "boids_cohesion_enabled": False,
            "evolution_enabled": False,
            "self_reflection": False
        },
        # 4. Single Loop + Boids - R3 (Cohesion only)
        {
            "name": "single_loop_boids_r3_cohesion",
            "boids_enabled": True,
            "boids_separation_enabled": False,
            "boids_alignment_enabled": False,
            "boids_cohesion_enabled": True,
            "evolution_enabled": False,
            "self_reflection": False
        },
        # 5. Single Loop + Boids - All (All rules)
        {
            "name": "single_loop_boids_all_rules",
            "boids_enabled": True,
            "boids_separation_enabled": True,
            "boids_alignment_enabled": True,
            "boids_cohesion_enabled": True,
            "evolution_enabled": False,
            "self_reflection": True  # Default with self-reflection
        },
        # 6. Single Loop + Boids - All + Evolutionary
        {
            "name": "single_loop_boids_all_evolution",
            "boids_enabled": True,
            "boids_separation_enabled": True,
            "boids_alignment_enabled": True,
            "boids_cohesion_enabled": True,
            "evolution_enabled": True,
            "self_reflection": False
        },
        # 7. Single Loop + Boids - All + Self-Reflection
        {
            "name": "single_loop_boids_all_self_reflection",
            "boids_enabled": True,
            "boids_separation_enabled": True,
            "boids_alignment_enabled": True,
            "boids_cohesion_enabled": True,
            "evolution_enabled": False,
            "self_reflection": True
        }
    ]
    
    for i, exp_config in enumerate(experiments, 1):
        logger.info(f"\n🔄 Running Experiment {i}/7: {exp_config['name']}")
        
        run_single_experiment(
            exp_name=exp_config['name'],
            meta_prompt=meta_prompt,
            num_agents=num_agents,
            num_rounds=num_rounds,
            boids_enabled=exp_config['boids_enabled'],
            boids_k=boids_k,
            boids_sep=boids_sep,
            boids_separation_enabled=exp_config['boids_separation_enabled'],
            boids_alignment_enabled=exp_config['boids_alignment_enabled'],
            boids_cohesion_enabled=exp_config['boids_cohesion_enabled'],
            evolution_enabled=exp_config['evolution_enabled'],
            evolution_frequency=evolution_frequency,
            evolution_selection_rate=evolution_selection_rate,
            self_reflection=exp_config['self_reflection'],
            model_name=model_name
        )
    
    logger.info("\n🎉 Ablation Study Complete!")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Run Formal Emergent Intelligence Experiments")
    parser.add_argument("--meta_prompt_id", required=True, help="The ID of the meta-prompt to use from meta_prompts.json")
    parser.add_argument("--num_agents", type=int, default=3, help="Number of agents in the society.")
    parser.add_argument("--num_rounds", type=int, default=10, help="Number of simulation rounds.")
    
    # Experiment mode selection
    parser.add_argument("--mode", choices=['single', 'ablation'], default='single', 
                       help="Run single experiment or complete ablation study")
    
    # Boids configuration
    parser.add_argument("--boids_enabled", action='store_true', help="Enable Boids rules for agent behavior.")
    parser.add_argument("--boids_k", type=int, default=2, help="Number of neighbors for Boids rules (k).")
    parser.add_argument("--boids_sep", type=float, default=0.45, help="Separation threshold for Boids rules.")
    
    # Individual boids rules (for single mode)
    parser.add_argument("--boids_separation", action='store_true', help="Enable separation rule")
    parser.add_argument("--boids_alignment", action='store_true', help="Enable alignment rule")
    parser.add_argument("--boids_cohesion", action='store_true', help="Enable cohesion rule")
    
    # Evolution configuration
    parser.add_argument("--evolution_enabled", action='store_true', help="Enable evolutionary algorithm")
    parser.add_argument("--evolution_frequency", type=int, default=5, help="Evolution frequency (rounds)")
    parser.add_argument("--evolution_selection_rate", type=float, default=0.2, help="Evolution selection rate")
    
    # Other features
    parser.add_argument("--self_reflection", action='store_true', help="Enable agent's self-reflection awareness (default: True)")
    parser.add_argument("--no_self_reflection", action='store_true', help="Disable agent's self-reflection awareness")
    
    # Model selection
    parser.add_argument("--model", choices=['default', 'gpt-4.1-nano', 'gpt-4o-mini', 'deepseek-v3'], 
                       default='default', help="Choose the LLM model to use for experiments")
    
    args = parser.parse_args()
    
    # Verify resources are accessible
    if not verify_resources():
        logger.error("❌ Resource verification failed. Please ensure all resource files are present.")
        return 1
    
    # Load enhanced meta-prompts
    meta_prompts = load_meta_prompts()
    if not meta_prompts:
        return 1
    
    selected_prompt = meta_prompts.get(args.meta_prompt_id)
    if not selected_prompt:
        logger.error(f"Meta-prompt ID '{args.meta_prompt_id}' not found in meta_prompts.json.")
        logger.info(f"Available IDs: {list(meta_prompts.keys())}")
        return 1
    
    if args.mode == 'ablation':
        # Run complete ablation study
        run_ablation_study(
            meta_prompt=selected_prompt,
            num_agents=args.num_agents,
            num_rounds=args.num_rounds,
            boids_k=args.boids_k,
            boids_sep=args.boids_sep,
            evolution_frequency=args.evolution_frequency,
            evolution_selection_rate=args.evolution_selection_rate,
            model_name=args.model
        )
    else:
        # Run single experiment
        # For single mode, if boids is enabled but no individual rules specified, enable all
        if args.boids_enabled and not any([args.boids_separation, args.boids_alignment, args.boids_cohesion]):
            boids_separation = boids_alignment = boids_cohesion = True
        else:
            boids_separation = args.boids_separation
            boids_alignment = args.boids_alignment
            boids_cohesion = args.boids_cohesion
        
        # Handle self-reflection: default to True unless explicitly disabled
        self_reflection = not args.no_self_reflection
        
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
            boids_sep=args.boids_sep,
            boids_separation_enabled=boids_separation,
            boids_alignment_enabled=boids_alignment,
            boids_cohesion_enabled=boids_cohesion,
            evolution_enabled=args.evolution_enabled,
            evolution_frequency=args.evolution_frequency,
            evolution_selection_rate=args.evolution_selection_rate,
            self_reflection=self_reflection,
            model_name=args.model
        )
    
    return 0


if __name__ == "__main__":
    exit(main()) 