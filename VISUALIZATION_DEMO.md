# 🎨 Boids Evolution Visualization Demo

This visualization demo brings your boids-evolution experiment to life with animated networks, interactive dashboards, and comprehensive reports.

## 🚀 Quick Start

### Option 1: Interactive Demo Runner
```bash
python run_demo.py
```
This will guide you through the visualization options with a simple menu.

### Option 2: Direct Command Line
```bash
# Install visualization dependencies
pip install -r requirements_viz.txt

# Run all visualizations
python demo_visualizer.py --all

# Or run specific visualizations
python demo_visualizer.py --animation    # Create animated GIF
python demo_visualizer.py --dashboard    # Create interactive HTML
python demo_visualizer.py --report       # Create summary report
```

## 📊 What You'll Get

### 1. 🎬 Animated Network Visualization
- **File**: `boids_evolution_animation.gif`
- **Shows**: Agent positions changing based on boids rules, tool creation events, evolution dynamics
- **Features**: Real-time boids behavior, tool creation "births", agent specialization

### 2. 🎛️ Interactive Dashboard  
- **File**: `boids_evolution_dashboard.html`
- **Shows**: Tool creation timeline, complexity distributions, collaboration networks
- **Features**: Hover interactions, zoom/pan, multi-plot analysis

### 3. 📊 Summary Report
- **File**: `evolution_summary_report.html`
- **Shows**: Comprehensive experiment statistics, agent performance, key insights
- **Features**: Beautiful HTML report, agent cards, performance metrics

## 🧬 What the Visualizations Show

### Boids Behavior in Action
- **Separation**: Agents move away from others with similar tools (creates diversity)
- **Alignment**: Agents move towards successful neighbors (spreads good strategies)
- **Cohesion**: Agents stay near the group center (maintains collaboration)

### Emergent Patterns
- **Tool Specialization**: Different agents focus on different tool types
- **Collaboration Networks**: Agents using each other's tools
- **Evolution Events**: Population changes and adaptation over time
- **Complexity Growth**: Tools becoming more sophisticated over rounds

## 🛠️ Technical Details

### Data Sources
The visualizer automatically detects and uses:
1. **Experiment Results**: From your `experiments/` directory
2. **Agent Tools**: Individual agent tool creation data
3. **Evolution History**: Population changes and selection events
4. **Synthetic Demo Data**: Generated if no experiment data found

### Visualization Features

#### Animated Network
- Agent positions updated using simplified boids physics
- Tool creation shown as expanding circles
- Agent size reflects tool count
- Color coding for different agents
- Statistics panel showing cumulative progress

#### Interactive Dashboard
- **Timeline Plot**: Tool creation over rounds by agent
- **Complexity Histogram**: Distribution of tool complexity scores
- **Network Graph**: Agent collaboration connections
- **Evolution Progress**: Complexity improvement over generations

#### Summary Report
- **Key Statistics**: Total tools, agents, rounds, average complexity
- **Agent Performance Cards**: Individual agent statistics and progress bars
- **Methodology Section**: Explanation of boids rules and experimental design
- **Key Insights**: Analysis of emergent behaviors observed

## 🎯 Customization Options

### Command Line Arguments
```bash
python demo_visualizer.py [options]

Options:
  --experiment-dir, -e    Path to experiment directory (default: experiments)
  --output-dir, -o        Output directory (default: visualizations)
  --animation, -a         Create animated visualization only
  --dashboard, -d         Create interactive dashboard only  
  --report, -r            Create summary report only
  --all                   Create all visualizations (default)
```

### Experiment Directory Detection
The visualizer will:
1. Look for the specified experiment directory
2. If it's a parent directory, use the most recent experiment
3. Generate synthetic demo data if no experiment data is found

## 🔧 Dependencies

### Required Packages
```
matplotlib>=3.5.0      # For animations and plots
networkx>=2.6.0        # For network analysis
plotly>=5.0.0          # For interactive visualizations
pandas>=1.3.0          # For data manipulation
numpy>=1.21.0          # For numerical computations
```

### Optional Packages
```
kaleido>=0.2.1         # For static plotly image export
pillow>=8.0.0          # For GIF creation
scikit-learn>=1.0.0    # For similarity calculations
ffmpeg-python>=0.2.0   # For video export
```

Install all at once:
```bash
pip install -r requirements_viz.txt
```

## 🎨 Visualization Examples

### What Each Visualization Tells You

#### 1. Animated Network
- **Agent Movement**: See boids rules in action as agents cluster and separate
- **Tool Creation**: Visual "births" when new tools are created
- **Specialization**: Agents of different colors focusing on different areas
- **Collaboration**: Connections between agents using each other's tools

#### 2. Interactive Dashboard
- **Timeline Analysis**: Which agents are most productive in each round?
- **Complexity Trends**: Are tools getting more sophisticated over time?
- **Collaboration Patterns**: Which agents work together most?
- **Evolution Impact**: How do population changes affect overall performance?

#### 3. Summary Report
- **Performance Comparison**: Which agents created the most/best tools?
- **Emergent Insights**: What patterns emerged from the boids rules?
- **Methodology Review**: How the experiment was designed and conducted
- **Key Findings**: What this tells us about emergent intelligence

## 🚀 Advanced Usage

### Using Your Own Experiment Data
1. Run your boids evolution experiment
2. Point the visualizer to your experiment directory:
   ```bash
   python demo_visualizer.py --experiment-dir path/to/your/experiment
   ```

### Customizing Colors and Styles
Edit the `agent_colors` dictionary in `demo_visualizer.py`:
```python
self.agent_colors = {
    'Agent_01': '#FF6B6B',  # Red
    'Agent_02': '#4ECDC4',  # Teal
    # Add more colors as needed
}
```

### Creating Custom Visualizations
The `BoidsEvolutionVisualizer` class can be extended with new methods:
```python
visualizer = BoidsEvolutionVisualizer('path/to/experiment')
# Add your custom visualization methods
visualizer.create_custom_plot()
```

## 🎯 Perfect For

- **Research Presentations**: Show emergent behavior in action
- **Academic Papers**: Compelling visual evidence of boids principles
- **Demos**: Interactive exploration of multi-agent systems
- **Education**: Teaching emergent intelligence and swarm behavior
- **Analysis**: Understanding what happened in your experiments

## 🔍 Troubleshooting

### Common Issues

**"No experiment data found"**
- The visualizer will generate synthetic demo data automatically
- Check that your experiment directory exists and contains results

**"Missing dependencies"**
- Run `pip install -r requirements_viz.txt`
- Or install packages individually as shown in error messages

**"Animation not working"**
- Ensure matplotlib backend supports animation
- Try: `pip install pillow` for GIF support

**"Interactive dashboard not opening"**
- The HTML file is saved but not automatically opened
- Manually open `visualizations/boids_evolution_dashboard.html` in your browser

### Performance Tips
- Large experiments (>50 agents) may take longer to animate
- Reduce animation frames by modifying the `max_rounds` parameter
- Use `--dashboard` only for faster interactive-only visualization

## 🎉 Example Output

After running the demo, you'll find in the `visualizations/` directory:
- `boids_evolution_animation.gif` - Animated network showing boids behavior
- `boids_evolution_dashboard.html` - Interactive analysis dashboard  
- `evolution_summary_report.html` - Comprehensive experiment report

Open the HTML files in your browser for interactive exploration!

---

*Created with ❤️ for the Boids Evolution project - making emergent intelligence visible!*

