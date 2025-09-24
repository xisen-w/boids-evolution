# Evolutionary Algorithm Integration

## Overview

The boids-evolution codebase now includes a **minimal evolutionary algorithm** that can be toggled on/off without impacting existing functionality. This feature enables Darwinian selection and evolution of agent populations based on tool complexity.

## Key Features

### 🔬 **Selection**
- Removes bottom 20% of agents based on average TCI (Tool Complexity Index) scores
- Ensures minimum population size is maintained
- Rankings are based on the complexity of tools agents have built

### 🧬 **Crossover** 
- Combines traits from two successful agents
- Uses Azure OpenAI to generate new `specific_prompt` specializations
- Creates hybrid agents that blend parent specializations

### 🔄 **Mutation**
- Varies successful agent traits to explore new directions
- Creates related but distinct specializations
- Higher temperature for more variation

### 📊 **Prompt-Based Evolution**
- Evolution occurs at the **prompt level**, not code level
- New agents get evolved `specific_prompt` specializations
- Leverages LLM creativity for generating novel agent behaviors

## Usage

### Basic Configuration

```python
from run_experiment import ExperimentRunner

runner = ExperimentRunner(
    experiment_name="my_evolutionary_experiment",
    num_agents=5,
    max_rounds=15,
    shared_meta_prompt="Your base prompt here",
    
    # Evolution settings
    evolution_enabled=True,           # Toggle evolution on/off
    evolution_frequency=5,            # Evolve every N rounds
    evolution_selection_rate=0.2      # Remove bottom 20%
)

success = runner.run_experiment()
```

### Advanced Configuration

```python
# In src/evolutionary_algorithm.py
evolutionary_algorithm = EvolutionaryAlgorithm(
    selection_rate=0.2,        # Fraction to eliminate
    mutation_rate=0.3,         # Probability of mutation
    crossover_rate=0.5,        # Probability of crossover vs mutation
    min_population_size=3      # Minimum agents to maintain
)
```

## How It Works

### 1. **Agent Evaluation**
- Calculates average TCI complexity score for each agent's tools
- Ranks agents from highest to lowest complexity
- Agents with no tools get score of 0.0

### 2. **Selection Process**
- Keeps top performers (e.g., top 80%)
- Eliminates bottom performers (e.g., bottom 20%)
- Maintains minimum population size for stability

### 3. **Agent Generation**
- For each eliminated agent, creates a replacement
- 50% chance of crossover (combine two parents)
- 50% chance of mutation (vary one parent)

### 4. **Prompt Evolution**
- **Crossover**: "Create a new agent specialization that combines the best aspects of both parents"
- **Mutation**: "Create a mutation of this specialization - keep it related but explore a different angle"

## Integration Points

### Zero Impact When Disabled
```python
evolution_enabled=False  # No impact on existing code
```

### Seamless Integration
- Plugs into existing `ExperimentRunner` 
- Works with both Boids and Legacy modes
- Preserves all existing functionality

### Evolution Timing
```python
# Evolution occurs between rounds
if (self.evolution_enabled and 
    round_num % self.evolution_frequency == 0 and 
    round_num < self.max_rounds):
    # Trigger evolution
```

## Testing

Run the test script to see evolution in action:

```bash
python test_evolutionary_experiment.py
```

This will run two experiments:
1. **Evolutionary**: With evolution enabled (12 rounds, evolve at rounds 5 & 10)
2. **Control**: Without evolution (same settings for comparison)

## Results & Analysis

### Evolution Summary
The system tracks and reports:
- Number of generations completed
- Complexity improvement over time
- Total agents eliminated/created
- Evolution history with timestamps

### Saved Data
All evolution data is automatically saved in experiment results:
```json
{
  "evolution_summary": {
    "generations": 2,
    "latest_avg_complexity": 4.2,
    "complexity_improvement": 1.8,
    "total_agents_eliminated": 2,
    "total_agents_created": 2,
    "evolution_history": [...]
  }
}
```

## Example Output

```
🧬 Evolution Generation 1
==================================================
🏆 Agent Rankings:
   1. Agent_3: 5.20 avg TCI (2 tools)
   2. Agent_1: 4.80 avg TCI (3 tools)
   3. Agent_2: 3.60 avg TCI (1 tools)
   4. Agent_4: 2.10 avg TCI (2 tools)
   5. Agent_5: 0.00 avg TCI (0 tools)

🔥 Selection: Keeping 4 survivors, eliminating 1
   Eliminated: ['Agent_5']

🧬 Mutation: EvoAgent_Gen1_1_Mut from Agent_3
   New specialization: Focus on advanced mathematical optimization tools...

🧬 Evolution complete: 4 survivors + 1 new agents
```

## Architecture Benefits

### 1. **Modular Design**
- Self-contained `EvolutionaryAlgorithm` class
- Clean separation of concerns
- Easy to extend or modify

### 2. **Configurable**
- All parameters are tunable
- Can be completely disabled
- Flexible evolution timing

### 3. **LLM-Powered**
- Leverages Azure OpenAI for creative evolution
- Generates human-readable specializations
- Maintains semantic coherence

### 4. **Data-Driven**
- Uses actual tool complexity metrics
- Objective fitness evaluation
- Comprehensive tracking and logging

This evolutionary layer adds a powerful dimension to the boids ecosystem, enabling populations to adapt and improve over time while maintaining full backward compatibility. 