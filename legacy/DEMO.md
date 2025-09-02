# 🎬 Boids Evolution Demo Guide

This guide shows you how to run the enhanced agent society simulation with beautiful visualizations and the new tool system.

## 🚀 Quick Start Demo

### 1. First Time Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up Azure OpenAI credentials
cp .env.example .env
# Edit .env with your actual Azure OpenAI credentials
```

### 2. Check Available Tools

Before running the simulation, see what tools are available:

```bash
python main_enhanced.py --show-tools
```

This will show:
- **Shared Tools**: Available to all agents (calculate, file_write, random_gen)
- **Personal Tools**: Created by individual agents (initially empty)

### 3. Run Basic Enhanced Demo

```bash
python main_enhanced.py --demo --agents 2 --rounds 2
```

This runs in **demo mode** with:
- 2 agents for simpler viewing
- 2 rounds to see progression
- Interactive pauses between steps
- Beautiful conversation visualization

## 🎯 Demo Features

### Enhanced Visualizations

1. **Agent Thinking Process** 🤔
   - Shows agent's current energy and success rate
   - Displays available tools
   - Thinking animation with dots

2. **Speech Bubble Conversations** 💬
   - Agents' communications in beautiful speech bubbles
   - Color-coded by agent (Cyan, Magenta, Yellow, etc.)
   - Proper text wrapping

3. **Action Parsing Display** 🔍
   - Shows how agent talk is interpreted
   - Confidence levels with visual indicators
   - Tool and parameter extraction

4. **Energy Bar Visualizations** 🔋
   - Visual energy bars for each agent
   - Color-coded energy gains/losses
   - Society-wide energy tracking

### Tool System Enhancements

1. **Shared Tools Directory** 📂
   ```
   shared_tools/
   ├── index.json          # Tool registry
   ├── calculate.py        # Math operations (+10 energy)
   ├── file_write.py       # File creation (+15 energy)
   └── random_gen.py       # Random values (+5 energy)
   ```

2. **Personal Tools** 👤
   ```
   personal_tools/
   └── Agent_01/
       ├── index.json      # Agent's tool registry
       └── [custom_tools]  # Agent-created tools
   ```

## 🎮 Demo Commands

### Basic Demo
```bash
python main_enhanced.py --demo
```
**What you'll see:**
- Interactive prompts between rounds
- Full conversation visualization
- 3 agents, 3 rounds
- Beautiful terminal output

### Quick Demo
```bash
python main_enhanced.py --agents 2 --rounds 2 --delay 0.5
```
**What you'll see:**
- Faster execution
- 2 agents for simpler viewing
- 0.5 second delays between rounds

### Quiet Mode
```bash
python main_enhanced.py --quiet --agents 3 --rounds 1
```
**What you'll see:**
- Minimal output
- Just the core results
- Good for testing

### Show Tools Only
```bash
python main_enhanced.py --show-tools
```
**What you'll see:**
- Complete tool registry
- Shared vs personal tools
- Energy rewards for each tool

## 🎨 What to Watch For

### 1. Talk → Act → Reward Flow

Each agent goes through this enhanced cycle:

```
🤔 Agent_01 is thinking...
   Energy: 0
   Available tools: 3
   Success rate: 0.0%
   ...
   ✨

💬 Agent_01 says:
┌──────────────────────────────────────────────────────────┐
│ Use calculate tool to add 15 and 27                     │
└──────────────────────────────────────────────────────────┘

🔍 Parsing Agent_01's communication...
   Tool: calculate
   Parameters: {'operation': 'add', 'a': 15, 'b': 27}
   🎯 Confidence: 85%

⚡ Agent_01's action result:
   ✅ Status: Success
   📝 Result: 15.0 add 27.0 = 42.0
   🔋 Energy gained: +10

   📈 Agent_01 Energy: 0 → 10 (+10)
```

### 2. Tool Discovery and Usage

- Agents see all available tools in their context
- They learn to specify tools by name
- Success rates improve over time
- Shared tools are used by all agents

### 3. Society Dynamics

Watch for:
- **Energy Competition**: Agents accumulate different energy levels
- **Tool Preferences**: Some agents prefer certain tools
- **Success Patterns**: Agents develop communication strategies
- **Collective Behavior**: Society-wide statistics evolve

### 4. Beautiful Terminal Output

- **Color-coded agents**: Each agent has a unique color
- **Status indicators**: ✅ ❌ 🎯 ⚡ 🔋 
- **Progress bars**: Visual energy levels
- **Organized sections**: Clear separation between phases

## 🛠️ Tool System Demo

### Current Shared Tools

1. **Calculate Tool** (+10 energy)
   - Operations: add, subtract, multiply, divide
   - Example: "Use calculate to add 5 and 3"

2. **File Write Tool** (+15 energy)  
   - Writes content to agent_outputs/ directory
   - Example: "Write 'Hello World' to greeting.txt"

3. **Random Generator** (+5 energy)
   - Random numbers or choices
   - Example: "Generate random number between 1 and 100"

### Future Personal Tools

The system is ready for agents to create their own tools, which will be stored in `personal_tools/Agent_XX/` directories.

## 🎯 Core Principle Demonstration

The demo clearly shows the fundamental principle:

> **If no one talks, nothing runs, and nobody gets reward. If someone talks, a tool runs, and energy increases.**

Watch how:
- Silent agents gain no energy
- Clear communication leads to successful actions
- Tool usage directly correlates with energy gain
- Society thrives when agents actively participate

## 🚀 Ready to Run?

1. **Set up your .env file** with Azure OpenAI credentials
2. **Run the demo**: `python main_enhanced.py --demo`
3. **Watch the magic**: Beautiful agent conversations and tool usage
4. **Experiment**: Try different agent counts and rounds

The enhanced system makes the **talk → act → reward** principle visually stunning and easy to understand! 