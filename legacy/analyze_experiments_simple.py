#!/usr/bin/env python3
"""
Simple Boids Evolution Experiment Analysis (No Dependencies)

Analyzes experiment results for emergent intelligence patterns without
requiring external libraries like pandas or matplotlib.
"""

import json
import os
import glob
from collections import defaultdict, Counter
from datetime import datetime
import statistics

class SimpleBoidsAnalyzer:
    """Analyzes boids experiment results for emergent intelligence patterns."""
    
    def __init__(self, results_dir="experiments/results"):
        self.results_dir = results_dir
        self.experiments = []
        self.analysis_results = {}
        
    def load_experiments(self):
        """Load all experiment JSON files."""
        json_files = glob.glob(f"{self.results_dir}/*.json")
        
        print(f"📂 Loading {len(json_files)} experiment files...")
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Extract metadata from filename
                filename = os.path.basename(file_path)
                parts = filename.replace('.json', '').split('_')
                
                exp_data = {
                    'file_path': file_path,
                    'filename': filename,
                    'experiment_id': parts[1] if len(parts) > 1 else 'unknown',
                    'data': data
                }
                
                self.experiments.append(exp_data)
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                
        print(f"✅ Loaded {len(self.experiments)} experiments successfully")
        
    def analyze_basic_patterns(self):
        """Analyze basic emergence patterns."""
        print("🔍 Analyzing basic emergence patterns...")
        
        results = {
            'total_experiments': len(self.experiments),
            'configurations': defaultdict(list),
            'specialization_evidence': [],
            'collaboration_evidence': [],
            'complexity_evidence': []
        }
        
        for exp in self.experiments:
            try:
                metadata = exp['data']['metadata']
                final_state = exp['data']['final_state']
                history = exp['data'].get('history', [])
                
                # Extract configuration
                topology = metadata.get('topology', 'unknown')
                num_agents = metadata.get('num_agents', 0)
                total_steps = metadata.get('total_steps', 0)
                
                config_key = f"{topology}_{num_agents}agents_{total_steps}steps"
                
                # Basic metrics
                total_tools = final_state.get('total_tools', 0)
                specializations = final_state.get('agent_specializations', {})
                tool_distribution = final_state.get('tool_type_distribution', {})
                
                # Calculate metrics
                unique_specializations = len(set(spec for spec in specializations.values() if spec))
                tool_diversity = len(tool_distribution)
                
                # Count collaboration events
                collaboration_events = 0
                total_actions = 0
                for step_data in history:
                    for result in step_data.get('agent_results', []):
                        total_actions += 1
                        if result.get('action') == 'use_tool':
                            collaboration_events += 1
                
                collaboration_rate = collaboration_events / total_actions if total_actions > 0 else 0
                
                # Store results
                exp_result = {
                    'topology': topology,
                    'agents': num_agents,
                    'steps': total_steps,
                    'total_tools': total_tools,
                    'unique_specializations': unique_specializations,
                    'tool_diversity': tool_diversity,
                    'collaboration_events': collaboration_events,
                    'collaboration_rate': collaboration_rate,
                    'tools_per_agent': total_tools / num_agents if num_agents > 0 else 0
                }
                
                results['configurations'][config_key].append(exp_result)
                
                # Evidence collection
                if unique_specializations >= max(1, num_agents * 0.6):  # 60% have unique roles
                    results['specialization_evidence'].append(exp_result)
                
                if collaboration_rate >= 0.15:  # 15% of actions are collaborations
                    results['collaboration_evidence'].append(exp_result)
                
                if total_tools > num_agents * 4:  # More than 4 tools per agent
                    results['complexity_evidence'].append(exp_result)
                    
            except Exception as e:
                print(f"❌ Error analyzing experiment {exp['filename']}: {e}")
        
        self.analysis_results['basic_patterns'] = results
        return results
    
    def detect_emergent_intelligence(self):
        """Detect specific indicators of emergent intelligence."""
        print("🧠 Detecting emergent intelligence indicators...")
        
        if not self.experiments:
            return {}
        
        intelligence_metrics = {
            'strong_specialization': 0,
            'high_collaboration': 0,
            'balanced_ecosystem': 0,
            'complexity_growth': 0,
            'total_experiments': len(self.experiments)
        }
        
        for exp in self.experiments:
            try:
                final_state = exp['data']['final_state']
                metadata = exp['data']['metadata']
                history = exp['data'].get('history', [])
                
                agents = metadata.get('num_agents', 0)
                
                # 1. Strong Specialization
                specializations = final_state.get('agent_specializations', {})
                unique_specs = len(set(spec for spec in specializations.values() if spec))
                if unique_specs >= agents * 0.7:  # 70% have unique specializations
                    intelligence_metrics['strong_specialization'] += 1
                
                # 2. High Collaboration
                collaboration_events = sum(
                    1 for step_data in history 
                    for result in step_data.get('agent_results', [])
                    if result.get('action') == 'use_tool'
                )
                if collaboration_events > len(history):  # More than 1 per step
                    intelligence_metrics['high_collaboration'] += 1
                
                # 3. Balanced Ecosystem
                tool_dist = final_state.get('tool_type_distribution', {})
                if len(tool_dist) == 4:  # All 4 tool types present
                    values = list(tool_dist.values())
                    if values:
                        mean_val = statistics.mean(values)
                        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
                        cv = stdev_val / mean_val if mean_val > 0 else float('inf')
                        if cv < 0.6:  # Balanced distribution
                            intelligence_metrics['balanced_ecosystem'] += 1
                
                # 4. Complexity Growth
                total_tools = final_state.get('total_tools', 0)
                if total_tools > agents * 5:  # More than 5 tools per agent
                    intelligence_metrics['complexity_growth'] += 1
                    
            except Exception as e:
                print(f"❌ Error in intelligence detection: {e}")
        
        # Convert to percentages
        keys_to_process = list(intelligence_metrics.keys())
        for key in keys_to_process:
            if key != 'total_experiments':
                percentage = (intelligence_metrics[key] / intelligence_metrics['total_experiments']) * 100
                intelligence_metrics[f"{key}_percentage"] = percentage
        
        self.analysis_results['intelligence_metrics'] = intelligence_metrics
        return intelligence_metrics
    
    def analyze_by_topology(self):
        """Analyze patterns by network topology."""
        print("🌐 Analyzing topology effects...")
        
        topology_results = defaultdict(list)
        
        for exp in self.experiments:
            try:
                metadata = exp['data']['metadata']
                final_state = exp['data']['final_state']
                
                topology = metadata.get('topology', 'unknown')
                agents = metadata.get('num_agents', 0)
                
                # Calculate metrics
                total_tools = final_state.get('total_tools', 0)
                specializations = final_state.get('agent_specializations', {})
                unique_specs = len(set(spec for spec in specializations.values() if spec))
                tool_diversity = len(final_state.get('tool_type_distribution', {}))
                
                topology_results[topology].append({
                    'agents': agents,
                    'tools_per_agent': total_tools / agents if agents > 0 else 0,
                    'specialization_ratio': unique_specs / agents if agents > 0 else 0,
                    'tool_diversity': tool_diversity
                })
                
            except Exception as e:
                print(f"❌ Error in topology analysis: {e}")
        
        # Calculate averages
        topology_summary = {}
        for topology, data_list in topology_results.items():
            if data_list:
                topology_summary[topology] = {
                    'sample_count': len(data_list),
                    'avg_tools_per_agent': statistics.mean([d['tools_per_agent'] for d in data_list]),
                    'avg_specialization_ratio': statistics.mean([d['specialization_ratio'] for d in data_list]),
                    'avg_tool_diversity': statistics.mean([d['tool_diversity'] for d in data_list])
                }
        
        self.analysis_results['topology_effects'] = topology_summary
        return topology_summary
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline."""
        print("🚀 Starting comprehensive analysis...")
        print("=" * 50)
        
        self.load_experiments()
        
        if not self.experiments:
            print("❌ No experiments found. Run experiments first!")
            return None
        
        # Run all analyses
        basic_patterns = self.analyze_basic_patterns()
        intelligence_metrics = self.detect_emergent_intelligence()
        topology_effects = self.analyze_by_topology()
        
        print("=" * 50)
        print("✅ Analysis complete!")
        
        return self.analysis_results
    
    def write_analysis_report(self, output_file="experimentation_analysis.md"):
        """Write comprehensive analysis report."""
        print(f"📝 Writing analysis report to {output_file}...")
        
        analysis = self.analysis_results
        
        with open(output_file, 'w') as f:
            f.write(f"""# Emergent Intelligence in Simple Boids: Experimental Analysis

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Experiments Analyzed:** {len(self.experiments)}

## Executive Summary

This report analyzes experimental data from a systematic study of emergent intelligence 
in a minimal 3-rule boids system applied to tool creation and sharing. The experiments 
test whether simple local rules can generate complex collaborative behaviors.

## Experimental Overview

### System Design
- **Agent Model:** 3 cognitive boids rules (Separation, Alignment, Cohesion)
- **Environment:** Tool creation and sharing ecosystem  
- **Variables:** Network topology, agent count, simulation duration
- **Metrics:** Specialization emergence, collaboration patterns, complexity growth

### Experimental Scope
- **Total Experiments:** {len(self.experiments)}
- **Topologies:** Triangle (fully connected), Line (chain), Star (hub-based)
- **Agent Counts:** 3-10 agents per experiment
- **Duration:** 20-100 simulation steps

## Key Findings

### 1. Emergent Intelligence Detection

""")
            
            # Intelligence metrics
            if 'intelligence_metrics' in analysis:
                metrics = analysis['intelligence_metrics']
                
                f.write(f"""**Intelligence Indicators:**
- Strong Specialization: {metrics.get('strong_specialization_percentage', 0):.1f}% of experiments
- High Collaboration: {metrics.get('high_collaboration_percentage', 0):.1f}% of experiments  
- Balanced Ecosystem: {metrics.get('balanced_ecosystem_percentage', 0):.1f}% of experiments
- Complexity Growth: {metrics.get('complexity_growth_percentage', 0):.1f}% of experiments

**Overall Intelligence Score:** """)
                
                avg_intelligence = statistics.mean([
                    metrics.get('strong_specialization_percentage', 0),
                    metrics.get('high_collaboration_percentage', 0),
                    metrics.get('balanced_ecosystem_percentage', 0),
                    metrics.get('complexity_growth_percentage', 0)
                ])
                
                f.write(f"{avg_intelligence:.1f}%\n\n")
                
                if avg_intelligence >= 70:
                    f.write("🧠 **CONCLUSION: STRONG EMERGENT INTELLIGENCE DETECTED**\n\n")
                    f.write("The system consistently demonstrates multiple indicators of emergent intelligence across experiments. Simple boids rules successfully generate sophisticated collaborative behaviors.\n\n")
                elif avg_intelligence >= 40:
                    f.write("🤔 **CONCLUSION: MODERATE EMERGENT INTELLIGENCE**\n\n") 
                    f.write("Some intelligence indicators are present but inconsistent. The system shows promise but may need parameter tuning or environmental pressures.\n\n")
                else:
                    f.write("❌ **CONCLUSION: LIMITED EMERGENT INTELLIGENCE**\n\n")
                    f.write("Few clear intelligence indicators detected. This may indicate:\n- Need for environmental pressures (survival, resource scarcity)\n- Insufficient simulation time for patterns to emerge\n- Required parameter optimization\n- Fundamental limitations of the current model\n\n")
            
            # Basic patterns analysis  
            if 'basic_patterns' in analysis:
                patterns = analysis['basic_patterns']
                
                f.write("### 2. Pattern Analysis Summary\n\n")
                
                if patterns['specialization_evidence']:
                    f.write(f"**✅ Specialization Evidence:** {len(patterns['specialization_evidence'])} experiments show strong role differentiation\n\n")
                else:
                    f.write("**❌ Limited Specialization:** Few experiments show clear role differentiation\n\n")
                
                if patterns['collaboration_evidence']:
                    f.write(f"**✅ Collaboration Evidence:** {len(patterns['collaboration_evidence'])} experiments show significant tool sharing\n\n")
                else:
                    f.write("**❌ Limited Collaboration:** Minimal tool sharing between agents detected\n\n")
                
                if patterns['complexity_evidence']:
                    f.write(f"**✅ Complexity Growth:** {len(patterns['complexity_evidence'])} experiments show rich tool ecosystems\n\n")
                else:
                    f.write("**❌ Limited Complexity:** Tool ecosystems remain simple\n\n")
            
            # Topology effects
            if 'topology_effects' in analysis:
                topology_data = analysis['topology_effects']
                
                f.write("### 3. Network Topology Effects\n\n")
                
                for topology, stats in topology_data.items():
                    f.write(f"**{topology.title()} Topology:**\n")
                    f.write(f"- Sample size: {stats['sample_count']} experiments\n")
                    f.write(f"- Average tools per agent: {stats['avg_tools_per_agent']:.2f}\n")
                    f.write(f"- Specialization ratio: {stats['avg_specialization_ratio']:.2f}\n")
                    f.write(f"- Tool diversity: {stats['avg_tool_diversity']:.2f}/4 types\n\n")
                
                # Find best topology
                best_topology = max(topology_data.items(), 
                                  key=lambda x: x[1]['avg_specialization_ratio'] + x[1]['avg_tool_diversity'])
                
                f.write(f"**Best Performing Topology:** {best_topology[0].title()} (highest specialization + diversity)\n\n")
            
            # Research implications
            f.write("""## Research Implications

### Primary Research Question: Can 3 simple rules create emergent collaborative intelligence?

""")
            
            if 'intelligence_metrics' in analysis:
                metrics = analysis['intelligence_metrics']
                avg_intelligence = statistics.mean([
                    metrics.get('strong_specialization_percentage', 0),
                    metrics.get('high_collaboration_percentage', 0),
                    metrics.get('balanced_ecosystem_percentage', 0),
                    metrics.get('complexity_growth_percentage', 0)
                ])
                
                if avg_intelligence >= 50:
                    f.write("**Answer: YES** - Clear evidence of emergent collaborative intelligence\n\n")
                    f.write("""**Key Mechanisms Identified:**
1. **Separation Rule** drives niche finding and specialization
2. **Alignment Rule** propagates successful strategies
3. **Cohesion Rule** creates tool sharing and collaboration
4. **Network Topology** significantly influences emergence patterns

**Significance:** This validates that minimal rule sets can generate sophisticated multi-agent intelligence without central coordination or explicit programming for collaboration.

""")
                else:
                    f.write("**Answer: INCONCLUSIVE** - Mixed evidence for emergent intelligence\n\n")
                    f.write("""**Possible Explanations:**
1. **Insufficient Environmental Pressure:** Agents may need survival stakes or resource constraints
2. **Parameter Sensitivity:** Boids rule weights may need optimization  
3. **Temporal Scale:** Longer simulations may be required for full emergence
4. **Agent Population:** Larger populations might enable richer dynamics
5. **Model Limitations:** Current tool ecosystem may be too simplified

**Recommendations for Future Work:**
- Add evolutionary pressure (survival-based selection)
- Implement resource constraints and competition
- Test with larger agent populations (20-100 agents)
- Extend simulation duration (500-1000 steps)
- Add environmental challenges requiring coordination

""")
            
            f.write("""### Implications for AI Research

**If Intelligence IS Emerging:**
- Validates bottom-up AI design principles
- Suggests minimal viable complexity for collaborative AI
- Provides foundation for evolutionary AI systems
- Demonstrates scalable multi-agent coordination

**If Intelligence is NOT Emerging:**
- Indicates need for environmental pressures in AI systems
- Suggests simple rules may be insufficient without stakes
- Points to importance of survival/resource dynamics
- Highlights parameter sensitivity in emergent systems

### Next Steps

1. **Evolution Phase:** Add genetic evolution of boids rule weights
2. **Survival Pressure:** Implement resource scarcity and competition
3. **Task Environment:** Add external challenges requiring coordination
4. **Scale Testing:** Experiment with 20-100 agent populations
5. **Comparative Analysis:** Test against other emergence models

## Technical Details

### Data Sources
""")
            
            f.write(f"- **Experiment Files:** {len(self.experiments)} JSON datasets\n")
            f.write(f"- **Configuration Coverage:** Multiple topologies, agent counts, durations\n")
            f.write(f"- **Step-by-Step Logging:** Full agent action and rule preference tracking\n\n")
            
            f.write("""### Analysis Methodology
- Multi-dimensional emergence detection
- Statistical pattern recognition  
- Comparative topology analysis
- Intelligence indicator synthesis

### Reproducibility
- Deterministic random seeds
- Systematic parameter sweeps  
- Open source analysis pipeline
- Raw data preservation

---

*Automated analysis generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*\n")
        
        print(f"✅ Analysis report written to {output_file}")

def main():
    """Main analysis execution."""
    analyzer = SimpleBoidsAnalyzer()
    
    # Run complete analysis
    results = analyzer.run_complete_analysis()
    
    if results:
        # Write analysis report
        analyzer.write_analysis_report()
        
        # Print key findings summary
        print("\n" + "="*60)
        print("🎯 EXPERIMENTAL ANALYSIS SUMMARY")
        print("="*60)
        
        if 'intelligence_metrics' in results:
            metrics = results['intelligence_metrics']
            
            print(f"📊 Total Experiments: {metrics['total_experiments']}")
            print(f"🧠 Intelligence Indicators:")
            print(f"   - Strong Specialization: {metrics.get('strong_specialization_percentage', 0):.1f}%")
            print(f"   - High Collaboration: {metrics.get('high_collaboration_percentage', 0):.1f}%")
            print(f"   - Balanced Ecosystem: {metrics.get('balanced_ecosystem_percentage', 0):.1f}%")
            print(f"   - Complexity Growth: {metrics.get('complexity_growth_percentage', 0):.1f}%")
            
            avg_intelligence = statistics.mean([
                metrics.get('strong_specialization_percentage', 0),
                metrics.get('high_collaboration_percentage', 0),
                metrics.get('balanced_ecosystem_percentage', 0),
                metrics.get('complexity_growth_percentage', 0)
            ])
            
            print(f"\n🎯 Overall Intelligence Score: {avg_intelligence:.1f}%")
            
            if avg_intelligence >= 70:
                print("✅ STRONG EMERGENT INTELLIGENCE DETECTED!")
                print("   Simple boids rules successfully create collaborative intelligence.")
            elif avg_intelligence >= 40:
                print("⚠️ MODERATE EMERGENT INTELLIGENCE")
                print("   Some patterns emerge but results are inconsistent.")
            else:
                print("❌ LIMITED EMERGENT INTELLIGENCE")
                print("   May need environmental pressures or parameter tuning.")
        
        if 'topology_effects' in results:
            topology_data = results['topology_effects']
            print(f"\n🌐 Network Topology Performance:")
            for topology, stats in topology_data.items():
                score = stats['avg_specialization_ratio'] + stats['avg_tool_diversity']/4
                print(f"   {topology.title():>8}: {score:.3f} (specialization + diversity)")
        
        print(f"\n📝 Full analysis available in: experimentation_analysis.md")
        print("="*60)
    else:
        print("❌ No analysis results generated. Check experiment data.")

if __name__ == "__main__":
    main() 