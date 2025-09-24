# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **boids evolution simulation** that demonstrates emergent intelligence through tool creation and collaboration. The system implements 3 simple boids rules (separation, alignment, cohesion) applied to agent societies that create tools and evolve capabilities.

## Common Commands

### Main Experiment Running
```bash
# Run real experiments (main entry point)
python3 run_real_experiment.py --meta_prompt_id "data_science_suite" --num_agents 3 --num_rounds 10

# Run with Boids rules enabled
python3 run_real_experiment.py --meta_prompt_id "data_science_suite" --num_agents 5 --num_rounds 15 --boids_enabled

# Configure Boids parameters
python3 run_real_experiment.py --meta_prompt_id "your_prompt_id" --boids_enabled --boids_k 3 --boids_sep 0.5
```

### Systematic Experiment Running
```bash
# Run systematic experiments (if available)
./run_experiments.sh

# Run specific experiment phases
./run_experiments.sh baseline
./run_experiments.sh scalability

# Alternative experiment runner
python3 run_experiment.py
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Dependencies: openai==1.51.0, python-dotenv==1.0.0, colorama==0.4.6
# Plus matplotlib and pandas for visualization
```

## Architecture Overview

The system is built around **emergent intelligence through tool creation**. All core components are located in the `src/` folder, with `run_real_experiment.py` as the main entry point.

### Core Components

**Agent System (`src/agent_v1.py`)**
- Core loop: observe → reflect → build_tools → build_tests
- Integrates with Azure OpenAI for AI-powered decision making
- Personal and shared tool registries

**Boids Rules (`src/boids_rules.py`)**
- Separation: Avoid building same tools as neighbors
- Alignment: Copy successful neighbors' strategies  
- Cohesion: Use neighbors' tools when possible
- Jaccard distance calculations for tool similarity

**Tool Registry (`src/tools_v1.py`)**
- Manages shared and personal tools with metadata
- Tool execution context and composition support
- File storage and importlib-based tool loading

**Evolutionary Algorithm (`src/evolutionary_algorithm.py`)**
- Selection based on tool complexity metrics
- Prompt-based mutation and crossover
- Population management and generation evolution

**Experiment Infrastructure**
- `ExperimentRunner` class for systematic testing
- `TCIAnalyzer` for complexity analysis
- `ExperimentVisualizer` for results visualization

### Tool Types
The system recognizes 4 main tool categories:
- `data`: Data processing and analysis tools
- `logic`: Decision making and reasoning tools  
- `utility`: General purpose utilities
- `connector`: Integration and communication tools

### Network Topologies
Supported agent network configurations:
- `triangle`: Each agent connected to 2 neighbors
- `line`: Linear chain of agents
- `star`: One central agent connected to all others

## Key Patterns

### Emergence Through Local Rules
Agents follow simple local rules but create complex collaborative patterns:
- **Specialization**: Agents naturally focus on different tool types
- **Collaboration**: Agents use each other's tools
- **Diversity**: All tool types emerge without central coordination

### Tool Ecosystem Evolution
- Tools build upon other tools (composition)
- Utility rewards flow to creators of foundational tools
- Community support drives tool development priorities

### Experiment-Driven Development
- Systematic exploration of parameter spaces
- Comprehensive logging and result analysis
- Statistical analysis of emergent behaviors

## File Organization

```
boids-evolution/
├── src/                          # All core implementation files
│   ├── agent_v1.py              # Main agent implementation
│   ├── boids_rules.py           # 3 boids rules logic
│   ├── tools_v1.py              # Tool registry and execution
│   ├── evolutionary_algorithm.py # Evolution mechanics
│   ├── azure_client.py          # OpenAI integration
│   ├── experiment_visualizer.py # Results visualization
│   ├── complexity_analyzer.py   # Tool complexity analysis (TCI)
│   └── environment_manager.py   # Environment setup
├── run_real_experiment.py       # MAIN ENTRY POINT
├── run_experiment.py            # Alternative experiment runner
├── meta_prompts.json            # Meta-prompts configuration
├── test_*.py                    # Test suites
├── experiments/                 # Generated experiment data
└── personal_tools/              # Agent-created tools storage
```

## Azure OpenAI Setup

For full functionality, configure Azure OpenAI:
1. Set environment variables: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`
2. Update `azure_client.py` with your deployment details
3. Use `.env` file for local development (python-dotenv support included)

## Testing Approach

The system includes comprehensive testing infrastructure:
- Unit tests for individual components (`test_*.py`)
- Integration tests for full experiment runs
- Agent-generated tests for created tools
- Evolutionary testing of tool combinations

## Data Output

Experiments generate JSON files with:
- Agent tool creation patterns
- Collaboration metrics
- Specialization emergence data  
- Tool composition networks
- Temporal evolution statistics

Use the generated data files for analysis of emergent behaviors and system performance.