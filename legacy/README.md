# Boids Evolution - Multi-Agent Tool Evolution System

An advanced **multi-agent evolutionary system** that combines **boids flocking behavior**, **genetic algorithms**, and **tool complexity analysis** to evolve sophisticated AI agent societies that create, test, and compose tools collaboratively.

## 🎯 Core Innovation: Boids + Evolution + Tool Complexity

**The breakthrough:** Agents follow **3 boids rules** for local coordination while a **genetic algorithm** evolves their specializations based on **Tool Complexity Index (TCI)** scores, creating emergent tool ecosystems of increasing sophistication.

### The 3 Boids Rules Applied to Tool Creation
```
1. ALIGNMENT:   Learn successful strategies from high-performing neighbors
2. SEPARATION:  Avoid building redundant tools, find unique niches  
3. COHESION:    Contribute to the global ecosystem trend and objectives
```

### Evolutionary Algorithm
- **Fitness Function**: Tool Complexity Index (TCI) scores (0-10 scale)
- **Selection**: Remove bottom 20% performers each generation
- **Reproduction**: Crossover (combine specializations) + Mutation (vary specializations)
- **Specialization Discovery**: Analyze agent behavior to update genetic code

### Tool Complexity Index (TCI)
```
TCI Score (0-10) = Code Complexity (0-3) + Interface Complexity (0-2) + Compositional Complexity (0-5)

- Code Complexity: Lines of code, algorithmic sophistication
- Interface Complexity: Parameter count, return structure complexity  
- Compositional Complexity: Tool calls to other agents' tools + external imports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API key (set in environment)
- Required packages: `pip install -r requirements.txt`

### Basic Usage

```bash
# Run a complete boids + evolution experiment
python run_real_experiment.py \
  --meta_prompt_id data_science_suite \
  --mode single \
  --num_agents 20 \
  --num_rounds 20 \
  --boids_enabled \
  --boids_k 2 \
  --boids_sep 0.45 \
  --evolution_enabled \
  --evolution_frequency 5 \
  --evolution_selection_rate 0.2
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--num_agents` | Population size | 10 |
| `--num_rounds` | Simulation rounds | 15 |
| `--boids_enabled` | Enable boids rules | True |
| `--boids_k` | Number of neighbors to observe | 2 |
| `--evolution_enabled` | Enable genetic algorithm | False |
| `--evolution_frequency` | Evolve every N rounds | 5 |
| `--evolution_selection_rate` | Fraction to eliminate | 0.2 |

### Available Meta-Prompts
```bash
# Data science tool suite
--meta_prompt_id data_science_suite

# Software development tools  
--meta_prompt_id software_dev_suite

# Machine learning pipeline
--meta_prompt_id ml_pipeline_suite
```



## 🏗️ System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                EXPERIMENT RUNNER                        │
│           (Orchestrates complete lifecycle)            │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────────────────┐
    │             │             │                         │
    ▼             ▼             ▼                         ▼
┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌──────────────────┐
│ AGENTS  │  │  TOOLS  │  │ EVOLUTION   │  │ COMPLEXITY       │
│ SYSTEM  │  │ SYSTEM  │  │ ALGORITHM   │  │ ANALYZER         │
└─────────┘  └─────────┘  └─────────────┘  └──────────────────┘
```

### Agent Lifecycle
```
1. OBSERVE → See neighbor tools and global ecosystem state
2. REFLECT → Apply boids rules to generate strategic thoughts  
3. BUILD_TOOLS → Create Python tools based on reflection
4. BUILD_TESTS → Generate and execute comprehensive tests
5. COMPLEXITY_ANALYSIS → Calculate TCI scores for fitness evaluation
```

### File Structure
```
boids-evolution/
├── src/
│   ├── agent_v1.py              # Advanced agent with tool creation
│   ├── evolutionary_algorithm.py # Genetic algorithm implementation
│   ├── tools_v1.py              # Tool registry and execution
│   ├── complexity_analyzer.py   # TCI complexity calculation
│   ├── boids_rules.py           # Boids behavior implementation
│   ├── azure_client.py          # LLM integration
│   └── environment_manager.py   # Package and capability management
├── experiments/                 # Experiment results and data
├── shared_tools_template/       # Initial tool templates
├── run_real_experiment.py       # Main experiment runner
├── meta_prompts.json           # Predefined mission objectives
└── requirements.txt            # Python dependencies
```

## 🧬 How Evolution Works

### 1. Initial Population
- 20 agents with shared meta-prompt (e.g., "build data science tools")
- Each agent gets unique specialization or starts generic
- Agents begin creating tools following boids rules

### 2. Fitness Evaluation
Every few rounds, agents are ranked by average TCI scores:
```python
# Example TCI breakdown:
Agent_01: TCI 2.4 (Code: 1.2, Interface: 0.8, Composition: 0.4)
Agent_02: TCI 1.8 (Code: 0.9, Interface: 1.0, Composition: 0.0)  
Agent_03: TCI 3.1 (Code: 1.5, Interface: 1.2, Composition: 0.4)
```

### 3. Selection & Reproduction
- **Eliminate** bottom 20% (lowest TCI agents)
- **Crossover**: Combine specializations from two successful agents
- **Mutation**: Vary successful agent's specialization
- **New Generation**: EvoAgent_Gen1_1_Cross, EvoAgent_Gen1_2_Mut, etc.

### 4. Specialization Discovery
Before evolution, analyze agent behavior to update their "genetic code":
```python
# Agent builds data validation tools → Update specialization:
"Focus on robust data validation and quality assurance tools with comprehensive error handling"
```

## 🐦 Boids Rules in Detail

### Alignment Rule
```
Learn from successful neighbors:
- Identify complexity leaders (highest TCI scores)
- Analyze their code patterns and design principles  
- Adopt successful strategies in your own tools
```

### Separation Rule  
```
Avoid redundancy:
- Use TF-IDF similarity analysis on neighbor tools
- Find unique functional niches
- Build complementary rather than duplicate tools
```

### Cohesion Rule
```
Align with ecosystem trends:
- Observe global summary of all agent activity
- Contribute to emerging collective patterns
- Support the overarching mission objective
```

## 📊 Tool Complexity Index (TCI)

### Calculation Formula
```python
def calculate_tci(tool_code):
    code_score = min(3.0, lines_of_code / 100.0)
    interface_score = min(2.0, (param_count / 5.0) + return_complexity)
    composition_score = min(5.0, (tool_calls * 0.5) + (external_imports * 0.1))
    
    return code_score + interface_score + composition_score
```

### Complexity Categories
- **0.0-2.0**: Simple standalone tools
- **2.0-4.0**: Moderate complexity with some composition
- **4.0-6.0**: Sophisticated tools with significant composition
- **6.0-8.0**: Highly complex compositional tools
- **8.0-10.0**: Maximum complexity architectures

### Example Tool Evolution
```python
# Generation 1: Simple tool (TCI: 1.2)
def execute(parameters, context=None):
    data = parameters.get('data')
    return {"result": data.mean()}

# Generation 5: Compositional tool (TCI: 4.8)  
def execute(parameters, context=None):
    data = parameters.get('data')
    if context:
        # Clean data first
        clean_result = context.call_tool('DataValidator', {'data': data})
        # Transform based on schema
        transform_result = context.call_tool('SchemaTransformer', {
            'data': clean_result['validated_data'],
            'schema': parameters.get('schema')
        })
        # Generate statistical summary
        stats = generate_advanced_statistics(transform_result['data'])
        return {
            "result": stats,
            "composition": "StatsTool -> DataValidator -> SchemaTransformer",
            "quality_score": clean_result['quality_score']
        }
    return {"result": data.mean()}  # Fallback
```

## 🔬 Research Applications

### Emergent Intelligence Studies
- **Collective Problem Solving**: How agent societies tackle complex challenges
- **Specialization Evolution**: Natural emergence of expert roles and niches
- **Tool Ecosystem Dynamics**: How compositional complexity grows over time

### AI Safety & Alignment
- **Cooperative AI Development**: Agents building tools for mutual benefit
- **Emergent Coordination**: Self-organizing without central control
- **Value Alignment**: Maintaining mission objectives across generations

### Software Engineering Research
- **Automated Tool Creation**: AI agents generating useful software tools
- **Compositional Architecture**: Building complex systems from simple components
- **Evolutionary Software Design**: Genetic algorithms for software evolution

## 📈 Example Experiment Results

### Complexity Evolution Over Time
```
Generation 0: Avg TCI 1.2 (simple standalone tools)
Generation 3: Avg TCI 1.8 (some external imports)  
Generation 6: Avg TCI 2.4 (beginning composition)
Generation 9: Avg TCI 3.2 (sophisticated tool chains)
```

### Specialization Emergence
```
Agent_01: "Data validation and quality assurance specialist"
Agent_05: "Statistical analysis and feature engineering expert"  
Agent_12: "Pipeline orchestration and workflow management"
EvoAgent_Gen3_2_Cross: "Hybrid validation + transformation specialist"
```

### Tool Ecosystem Growth
```
Round 1:  20 tools  (all standalone)
Round 10: 180 tools (15% compositional) 
Round 20: 400 tools (32% compositional)
```

## 🛠️ Advanced Usage

### Custom Meta-Prompts
```python
# Add to meta_prompts.json:
{
  "custom_domain": {
    "prompt": "Build specialized tools for [your domain]",
    "description": "Custom mission objective"
  }
}
```

### Experiment Configuration
```python
# Custom experiment parameters
experiment = ExperimentRunner(
    experiment_name="custom_evolution",
    num_agents=15,
    max_rounds=25, 
    boids_enabled=True,
    boids_k_neighbors=3,
    evolution_enabled=True,
    evolution_frequency=4,
    evolution_selection_rate=0.15
)
```

### Analysis Tools
```bash
# Analyze experiment results
python experiment_result_analyzer.py experiments/your_experiment/

# Generate visualizations  
python -m src.experiment_visualizer experiments/your_experiment/
```

## 🎯 Key Insights

### 1. **Boids + Evolution = Emergent Sophistication**
Local coordination rules combined with global evolutionary pressure creates increasingly sophisticated tool ecosystems.

### 2. **Compositional Complexity Drives Evolution**  
Agents that learn to build on others' tools achieve higher fitness and evolutionary success.

### 3. **Specialization Through Selection Pressure**
Genetic algorithms naturally create specialist agents with distinct tool-building niches.

### 4. **Tool Ecosystem Network Effects**
More compositional tools enable even more sophisticated compositions in future generations.

### 5. **Emergent Collaboration Without Central Planning**
Agents learn to use each other's tools through boids alignment and ecosystem cohesion.

## 🚀 Future Directions

### v2.0: Multi-Objective Evolution
- Fitness functions beyond complexity (reliability, adoption, efficiency)
- Pareto-optimal tool evolution across multiple objectives
- Dynamic fitness landscape adaptation

### v3.0: Meta-Learning Agents  
- Agents that learn how to learn tool creation strategies
- Self-modifying genetic algorithms
- Emergent innovation in tool design patterns

### v4.0: Large-Scale Societies
- Hundreds of agents with hierarchical organization
- Specialized tool guilds and collaborative projects
- Cultural evolution of tool-building practices

---

## 📊 Citation

If you use this system in research, please cite:

```bibtex
@software{boids_evolution_2024,
  title={Boids Evolution: Multi-Agent Tool Evolution with Emergent Intelligence},
  author={[Your Name]},
  year={2024},
  url={https://github.com/your-repo/boids-evolution}
}
```

**Experience emergent intelligence through the evolution of collaborative AI agent societies!** 🚀 
