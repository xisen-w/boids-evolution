# Boids Evolution v0.0 - Agent Society with Recursive Tool Composition

A breakthrough implementation of emergent intelligence through **recursive tool composition** where agents create, share, and build upon each other's tools. This system demonstrates how simple **talk → act → reward** loops can evolve into complex adaptive behaviors when tools can call other tools.

## 🎯 Core Innovation: Recursive Tool Ecosystem

**The key breakthrough:** Tools can call other tools during execution, creating a recursive ecosystem where agents are rewarded for building useful foundations that others build upon.

### The Fundamental Loop
```
Agent talks → Tool executes → Tool calls other tools → Utility rewards flow back to creators
```

**Example Tool Composition:**
- Agent A creates `multiply(a, b)` tool
- Agent B creates `square(n)` tool that uses `multiply(n, n)`
- Agent C uses `square(5)` → Agent A gets utility reward for `multiply` being used

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI account with GPT-4 deployment
- Virtual environment (recommended)

### Installation

1. **Clone and setup**:
```bash
git clone <your-repo-url>
cd boids-evolution
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Azure OpenAI**:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

3. **Run the demo**:
```bash
python main.py --demo --agents 2 --rounds 2
```

## 🎮 Usage Examples

### Basic Demo (Enhanced Mode)
```bash
python main.py --demo
```
**Features:** Interactive demo with full tool composition visualization, utility rewards, and recursive calling.

### Simple Mode (Without Visualizations)
```bash
python main.py --simple --agents 3 --rounds 3
```
**Features:** Core functionality without complex visualizations, good for understanding the base mechanics.

### Show Available Tools
```bash
python main.py --show-tools
```
**Features:** Display all available tools, their dependencies, and reward structures.

### Custom Configuration
```bash
python main.py --agents 4 --rounds 5 --delay 0.5
```

## 🧠 How Recursive Tool Composition Works

### Tool Execution Context
Every tool execution gets a `ToolExecutionContext` that enables:
- **Recursive calling**: Tools can call other tools via `context.call_tool()`
- **Reward propagation**: Utility rewards flow to tool creators
- **Dependency tracking**: Full execution traces and dependency graphs
- **Circular detection**: Prevents infinite recursion
- **Depth limiting**: Configurable maximum call depth

### Example: Building Complex Math from Simple Tools

1. **Foundation Tool** (`multiply.py`):
```python
def execute(parameters, context=None):
    a = float(parameters.get('a', 0))
    b = float(parameters.get('b', 0))
    result = a * b
    return {
        'success': True,
        'result': f'{a} * {b} = {result}',
        'numeric_result': result,
        'energy_gain': 8
    }
```

2. **Composed Tool** (`square.py`):
```python
def execute(parameters, context=None):
    number = float(parameters.get('number', 0))
    
    # Call the multiply tool for composition
    multiply_result = context.call_tool('multiply', {'a': number, 'b': number})
    
    if multiply_result['success']:
        return {
            'success': True,
            'result': f'Square of {number} = {multiply_result["numeric_result"]}',
            'energy_gain': 12,
            'composition': f'square({number}) = multiply({number}, {number})'
        }
```

3. **Complex Tool** (`power.py`):
```python
def execute(parameters, context=None):
    base = float(parameters.get('base', 0))
    exponent = int(parameters.get('exponent', 1))
    
    # Use repeated multiplication for composition
    result = base
    for i in range(exponent - 1):
        multiply_result = context.call_tool('multiply', {'a': result, 'b': base})
        if multiply_result['success']:
            result = multiply_result['numeric_result']
    
    return {
        'success': True,
        'result': f'{base}^{exponent} = {result}',
        'energy_gain': 15,
        'operations_count': exponent - 1
    }
```

### Reward Propagation Example
When Agent C uses `power(2, 3)`:
1. **Primary reward**: Agent C gets +15 energy for successful power operation
2. **Utility rewards**: Creator of `multiply` tool gets +2 energy (×2 for two multiply calls)
3. **Cascading rewards**: Complex tools can create deep reward chains

## 🏗️ Architecture

### Project Structure
```
boids-evolution/
├── src/
│   ├── enhanced_agent.py           # Agent with recursive tool support
│   ├── tool_execution_context.py   # Context for recursive execution
│   ├── enhanced_tools.py           # Dynamic tool registry
│   ├── conversation_visualizer.py  # Beautiful conversation display
│   └── azure_client.py             # Azure OpenAI integration
├── shared_tools/
│   ├── index.json                  # Tool registry database
│   ├── calculate.py                # Basic math operations
│   ├── multiply.py                 # Foundation multiplication
│   ├── square.py                   # Composed tool using multiply
│   ├── power.py                    # Complex tool using multiply repeatedly
│   ├── file_write.py               # File operations
│   └── random_gen.py               # Random number generation
├── personal_tools/                 # Agent-specific tools
├── venv/                          # Virtual environment
├── main.py                        # Unified entry point
├── requirements.txt               # Dependencies
└── .env.example                  # Configuration template
```

### Key Components

#### 1. ToolExecutionContext
The heart of recursive tool calling:
- **`call_tool(tool_name, parameters)`**: Execute another tool
- **Circular dependency detection**: Prevents infinite loops
- **Reward tracking**: Automatically distributes utility rewards
- **Execution tracing**: Full logs of tool composition chains

#### 2. Enhanced Agent
Agents that understand tool composition:
- **Context-aware execution**: All tool calls include execution context
- **Utility reward processing**: Automatically receives rewards when their tools are used
- **Beautiful visualization**: Shows tool composition in real-time

#### 3. Tool Registry
Dynamic loading of tools with dependency tracking:
- **Shared tools**: Available to all agents
- **Personal tools**: Agent-specific creations
- **Dependency resolution**: Tracks which tools depend on others
- **Usage statistics**: Monitors tool popularity

## 🎨 What You'll See in Action

### 1. Agent Thinking Process
```
🤔 Agent_01 is thinking...
   Energy: 15
   Available tools: 6
   Success rate: 85.7%
   ...
   ✨
```

### 2. Beautiful Speech Bubbles
```
💬 Agent_01 says:
┌──────────────────────────────────────────────────────────┐
│ Use square tool to calculate 5 squared                  │
└──────────────────────────────────────────────────────────┘
```

### 3. Tool Composition Visualization
```
🔍 Parsing Agent_01's communication...
   Tool: square
   Parameters: {'number': 5}
   🎯 Confidence: 90%

⚡ Agent_01's action result:
   ✅ Status: Success
   📝 Result: Square of 5 = 25 (using multiply tool)
   🔋 Energy gained: +12

   🔗 Tool Composition: square → multiply
   📊 Depth: 1, Total calls: 1
   💰 Utility rewards distributed:
      → system: +2
```

### 4. Utility Reward Distribution
```
💰 UTILITY REWARDS SUMMARY:
   Agent_01: +0 (tools used by others)
   Agent_02: +6 (multiply tool used 3 times)
   system: +4 (foundational tools used)
```

## 🔬 Research Implications

This implementation validates several breakthrough concepts:

### 1. Emergent Tool Ecosystems
- **Composability**: Simple tools become building blocks for complex operations
- **Specialization**: Agents develop expertise in creating foundational vs. complex tools
- **Natural selection**: Useful tools get used more, creating evolutionary pressure

### 2. Reward Propagation Economics
- **Utility rewards**: Creators of foundational tools get sustained income
- **Incentive alignment**: Building useful foundations becomes profitable
- **Recursive value creation**: Complex tools create value for entire dependency chains

### 3. Collaborative Intelligence
- **Tool sharing**: Individual creations benefit the entire society
- **Compositional complexity**: Simple rules lead to sophisticated behaviors
- **Decentralized evolution**: No central planning, yet coherent progress emerges

### 4. Scalable Architecture
- **Modular design**: Easy to add new tools and capabilities
- **Recursive execution**: Arbitrary depth tool composition
- **Context preservation**: Full execution traces for debugging and analysis

## 🎯 Core Principles Demonstrated

### Talk → Act → Reward Enhanced
The basic loop is amplified by recursive composition:

1. **Talk**: Agents communicate intent to use tools
2. **Act**: Tools execute, potentially calling other tools
3. **Reward**: Energy flows to direct users AND tool creators
4. **Propagate**: Utility rewards create incentives for useful tool creation

### Survival of the Useful
- **Tool creators** prosper when their tools become building blocks
- **Tool users** benefit from rich ecosystem of available capabilities  
- **Tool composition** creates emergent behaviors beyond individual components
- **Society evolution** happens through useful tool propagation

## 🛣️ Future Extensions

From this v0.0 foundation, natural progressions include:

### v0.1: Advanced Tool Creation
- **Agent-generated tools**: Agents write their own tools using LLMs
- **Dynamic parameters**: Tools that adapt their interfaces
- **Tool testing**: Automatic validation of agent-created tools

### v0.2: Tool Markets
- **Energy trading**: Agents trade energy for tool access
- **Tool licensing**: Creators set prices for tool usage
- **Reputation systems**: Trust metrics for tool reliability

### v0.3: Evolutionary Pressure
- **Tool mutation**: Variations on existing tools
- **Performance optimization**: Tools that evolve to be more efficient
- **Ecosystem dynamics**: Tools compete for usage and resources

### v0.4: Multi-Agent Collaboration
- **Collaborative tool creation**: Multiple agents building tools together
- **Tool fusion**: Combining multiple tools into new capabilities
- **Emergent protocols**: Agents developing communication standards

### v1.0: Full Boids-Style Evolution
- **Spatial dynamics**: Tool propagation through agent networks
- **Local interaction**: Agents learn from nearby tool usage
- **Global emergence**: Society-wide patterns from local tool sharing

## 🤝 Contributing

This system is designed for extensibility:

### Adding New Tools
1. Create tool file in `shared_tools/`
2. Update `shared_tools/index.json`
3. Implement `execute(parameters, context=None)` function
4. Use `context.call_tool()` for composition

### Tool Development Guidelines
- **Context awareness**: Always accept `context` parameter
- **Error handling**: Graceful fallbacks when dependencies fail
- **Return format**: Standard `{'success': bool, 'result': str, 'energy_gain': int}`
- **Composition logging**: Use `context` for dependency tracking

## 📊 Example Session Output

```bash
$ python main.py --demo --agents 2 --rounds 2

🤖 Boids Evolution v0.0 - Enhanced Agent Society
============================================================
✨ Features: Recursive Tool Composition, Reward Propagation
🎯 Core: Talk → Act → Reward
🔗 Tools can call other tools, creating emergent complexity

🔧 AVAILABLE TOOLS (6 total)
==================================================

📂 SHARED TOOLS (6):
  • calculate: Perform mathematical calculations (+10 energy)
  • multiply: Basic multiplication - foundational tool (+8 energy)
  • square: Square using multiply tool (+12 energy) [depends: multiply]
  • power: Calculate power using repeated multiplication (+15 energy) [depends: multiply]
  • file_write: Write content to files (+15 energy)
  • random_gen: Generate random numbers or choices (+5 energy)

🎯 Core Principle: Talk → Act → Reward
✨ Enhanced with RECURSIVE TOOL COMPOSITION
💰 Tool creators get utility rewards when their tools are used by others

Press Enter to start the demo...

============================================================
🤖 ROUND 1 - Enhanced Agent Society with Tool Composition
============================================================

>>> Agent_01 Turn

🤔 Agent_01 is thinking...
   Energy: 0
   Available tools: 6
   Success rate: 0.0%
   ...
   ✨

💬 Agent_01 says:
┌──────────────────────────────────────────────────────────┐
│ Use square tool to calculate the square of 7            │
└──────────────────────────────────────────────────────────┘

🔍 Parsing Agent_01's communication...
   Tool: square
   Parameters: {'number': 7}
   🎯 Confidence: 85%

⚡ Agent_01's action result:
   ✅ Status: Success
   📝 Result: Square of 7 = 49 (using multiply tool)
   🔋 Energy gained: +12

   🔗 Tool Composition: square → multiply
   📊 Depth: 1, Total calls: 1
   💰 Utility rewards distributed:
      → system: +2

   📈 Agent_01 Energy: 0 → 12 (+12)

📊 Agent_01 Cycle Complete
──────────────────────────
```

## 🎉 Get Started Today!

1. **Set up your environment** with Azure OpenAI credentials
2. **Run the demo**: `python main.py --demo`
3. **Watch tool composition** create emergent complexity
4. **Experiment** with different agent configurations
5. **Build new tools** that compose with existing ones

The recursive tool ecosystem transforms simple agent communication into a rich, evolving society where useful contributions are automatically rewarded and complex behaviors emerge naturally! 🚀 
