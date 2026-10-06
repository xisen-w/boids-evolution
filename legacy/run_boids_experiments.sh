#!/bin/bash

# ==============================================================================
# Boids-Evolution Experiment Runner - Focused Boids Experiment Script
# ==============================================================================
# This script runs a focused set of experiments with Boids dynamics enabled
# for 3 representative meta-prompt scenarios.
#
# Standard Configuration: 20 Agents, 15 Rounds, Boids Enabled
# ==============================================================================

# Activate the project's virtual environment to ensure correct dependencies
source venv/bin/activate

echo "🚀 Launching 3 Boids experiments in parallel..."
echo "Standard Configuration: 20 Agents, 15 Rounds, Boids Enabled (k=2, sep=0.45)"
echo "Monitor individual experiment logs for progress. This will take a while."
echo "----------------------------------------------------------------------"

# Define the standard experiment parameters
NUM_AGENTS=20
NUM_ROUNDS=15

# Array of 3 representative meta-prompt IDs from meta_prompts.json
SCENARIOS=(
    "data_science_suite"
    "code_generation_toolkit"
    "file_system_organizer"
)

# Loop through each scenario and launch the experiment as a background process
for SCENARIO_ID in "${SCENARIOS[@]}"
do
    echo "   ▶️  Starting Boids experiment for scenario: $SCENARIO_ID"
    python3 run_real_experiment.py \
        --meta_prompt_id "$SCENARIO_ID" \
        --num_agents $NUM_AGENTS \
        --num_rounds $NUM_ROUNDS \
        --boids_enabled &
done

# The 'wait' command is crucial. It tells the script to wait until all
# background jobs (the experiments launched with '&') are finished.
echo "----------------------------------------------------------------------"
echo "✅ All Boids experiments launched. Waiting for all processes to complete..."

wait

echo "🎉 All 3 Boids experiments have completed successfully!"
echo "----------------------------------------------------------------------" 