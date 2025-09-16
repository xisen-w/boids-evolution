#!/usr/bin/env python3
"""
Comprehensive Experiment Result Analyzer
========================================

A rigorous analysis tool for boids-evolution experiments that extracts 
multi-dimensional insights to showcase emergent intelligence across various facets.

Usage:
    python experiment_result_analyzer.py <experiment_directory>
    
Example:
    python experiment_result_analyzer.py experiments/exp_boids_data_science_suite_20250916_090900
"""

import os
import json
import re
import ast
import math
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("⚠️ WordCloud not available - install with: pip install wordcloud")

# Import our complexity analyzer
from src.complexity_analyzer import TCILiteAnalyzer


@dataclass
class ToolMetrics:
    """Comprehensive metrics for a single tool."""
    name: str
    agent_id: str
    round_created: int
    lines_of_code: int = 0
    function_count: int = 0
    parameter_count: int = 0
    return_complexity: int = 0
    imports_count: int = 0
    tool_calls: int = 0
    test_passed: bool = False
    test_execution_success: bool = False
    tci_score: float = 0.0
    code_complexity: float = 0.0
    interface_complexity: float = 0.0
    compositional_complexity: float = 0.0
    semantic_category: str = ""
    description_length: int = 0
    unique_words: int = 0
    adoption_count: int = 0


@dataclass
class AgentProfile:
    """Comprehensive profile for an agent."""
    agent_id: str
    total_tools: int = 0
    total_reflections: int = 0
    specialization_score: float = 0.0
    avg_complexity: float = 0.0
    innovation_index: float = 0.0
    collaboration_score: float = 0.0
    consistency_score: float = 0.0
    tool_categories: List[str] = field(default_factory=list)
    complexity_trajectory: List[float] = field(default_factory=list)
    strategic_evolution: List[str] = field(default_factory=list)


@dataclass
class EcosystemMetrics:
    """System-level emergent intelligence metrics."""
    total_tools: int = 0
    category_entropy: float = 0.0
    loc_consistency: float = 0.0
    redundancy_rate: float = 0.0
    collaboration_density: float = 0.0
    unique_pattern_ratio: float = 0.0
    agent_complexity_variance: float = 0.0
    category_concentration: float = 0.0
    center_drift_rate: float = 0.0


class ExperimentAnalyzer:
    """Comprehensive analyzer for boids-evolution experiments."""
    
    def __init__(self, experiment_dir: str):
        self.exp_dir = Path(experiment_dir)
        self.tci_analyzer = TCILiteAnalyzer()
        
        # Analysis results
        self.tool_metrics: List[ToolMetrics] = []
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.ecosystem_metrics: EcosystemMetrics = EcosystemMetrics()
        self.temporal_data: Dict[str, List] = defaultdict(list)
        
        # Semantic categorization patterns
        self.category_patterns = {
            'data_profiling': ['profile', 'summary', 'describe', 'explore', 'analyze'],
            'data_cleaning': ['clean', 'preprocess', 'transform', 'normalize', 'validate'],
            'pipeline_orchestration': ['pipeline', 'orchestrat', 'workflow', 'engine', 'controller'],
            'visualization': ['visual', 'plot', 'chart', 'dashboard', 'display'],
            'api_service': ['api', 'service', 'endpoint', 'gateway', 'interface'],
            'validation': ['validat', 'check', 'verify', 'test', 'quality'],
            'registry': ['registry', 'hub', 'repository', 'catalog', 'store'],
            'monitoring': ['monitor', 'alert', 'detect', 'track', 'watch'],
            'governance': ['governance', 'policy', 'compliance', 'trust', 'audit']
        }
    
    def analyze_experiment(self) -> Dict[str, Any]:
        """Run comprehensive analysis of the experiment."""
        print(f"🔬 Analyzing experiment: {self.exp_dir.name}")
        
        # Load experiment data
        self._load_experiment_metadata()
        self._load_results_data()
        self._analyze_tools()
        self._analyze_agents()
        self._analyze_ecosystem()
        self._analyze_temporal_patterns()
        
        # Generate visualizations
        self._create_complexity_visualizations()
        self._create_ecosystem_visualizations()
        self._create_agent_analysis()
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report()
        
        print(f"✅ Analysis complete! Results saved in: {self.exp_dir}/analysis_results/")
        return report
    
    def _load_experiment_metadata(self):
        """Load experiment configuration and metadata."""
        metadata_file = self.exp_dir / 'experiment_metadata.json'
        results_file = self.exp_dir / 'results.json'
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        else:
            raise FileNotFoundError(f"Results file not found: {results_file}")
    
    def _load_results_data(self):
        """Extract core metrics from results.json."""
        self.final_stats = self.results.get('final_statistics', {})
        self.round_results = self.results.get('round_results', [])
        self.agent_summaries = self.results.get('agent_summaries', {})
        self.center_history = self.results.get('center_history', [])
    
    def _analyze_tools(self):
        """Comprehensive analysis of all tools created."""
        print("📊 Analyzing tool ecosystem...")
        
        personal_tools_dir = self.exp_dir / 'personal_tools'
        
        if not personal_tools_dir.exists():
            print("⚠️ No personal_tools directory found")
            return
        
        for agent_dir in personal_tools_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith('_'):
                continue
                
            agent_id = agent_dir.name
            index_file = agent_dir / 'index.json'
            
            if not index_file.exists():
                continue
            
            try:
                with open(index_file, 'r') as f:
                    agent_data = json.load(f)
                
                # Analyze each tool
                for tool_name, tool_info in agent_data.get('tools', {}).items():
                    tool_file = agent_dir / tool_info['file']
                    
                    if tool_file.exists():
                        metrics = self._analyze_single_tool(
                            tool_file, tool_info, agent_id
                        )
                        self.tool_metrics.append(metrics)
            except Exception as e:
                print(f"⚠️ Failed to process {agent_id}: {e}")
    
    def _analyze_single_tool(self, tool_file: Path, tool_info: Dict, agent_id: str) -> ToolMetrics:
        """Analyze a single tool file comprehensively."""
        metrics = ToolMetrics(
            name=tool_info['name'],
            agent_id=agent_id,
            round_created=tool_info.get('created_in_round', 1),
            test_passed=tool_info.get('test_passed', False),
            test_execution_success=tool_info.get('test_execution_success', False),
            adoption_count=tool_info.get('adoption_count', 0),
            description_length=len(tool_info.get('description', ''))
        )
        
        # Analyze code structure
        try:
            with open(tool_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Basic metrics
            metrics.lines_of_code = len([line for line in code.split('\n') if line.strip()])
            
            # AST analysis for deeper insights
            try:
                tree = ast.parse(code)
                
                # Count functions
                metrics.function_count = len([node for node in ast.walk(tree) 
                                            if isinstance(node, ast.FunctionDef)])
                
                # Count parameters (from main execute function)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == 'execute':
                        metrics.parameter_count = len(node.args.args)
                        break
                
                # Count imports
                metrics.imports_count = len([node for node in ast.walk(tree) 
                                           if isinstance(node, (ast.Import, ast.ImportFrom))])
                
                # Count return statements (complexity indicator)
                metrics.return_complexity = len([node for node in ast.walk(tree) 
                                               if isinstance(node, ast.Return)])
                
            except SyntaxError:
                pass  # Handle malformed code gracefully
            
            # TCI Analysis using our complexity analyzer
            try:
                # Create a temporary directory structure for TCI analysis
                temp_dir = tool_file.parent
                tci_results = self.tci_analyzer.analyze_tools_directory(str(temp_dir))
                
                tool_tci = tci_results.get(agent_id, {}).get(metrics.name, {})
                if tool_tci:
                    metrics.tci_score = tool_tci.get('tci_score', 0.0)
                    metrics.code_complexity = tool_tci.get('code_complexity', 0.0)
                    metrics.interface_complexity = tool_tci.get('interface_complexity', 0.0)
                    metrics.compositional_complexity = tool_tci.get('compositional_complexity', 0.0)
            
            except Exception as e:
                print(f"⚠️ TCI analysis failed for {metrics.name}: {e}")
            
        except Exception as e:
            print(f"⚠️ Failed to analyze {tool_file}: {e}")
        
        # Semantic categorization
        metrics.semantic_category = self._categorize_tool(metrics.name, tool_info.get('description', ''))
        
        # Description analysis
        description = tool_info.get('description', '').lower()
        metrics.unique_words = len(set(re.findall(r'\b\w+\b', description)))
        
        return metrics
    
    def _categorize_tool(self, name: str, description: str) -> str:
        """Categorize tool based on name and description."""
        text = (name + ' ' + description).lower()
        
        category_scores = {}
        for category, patterns in self.category_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'other'
    
    def _analyze_agents(self):
        """Analyze individual agent behaviors and patterns."""
        print("🤖 Analyzing agent behaviors...")
        
        for agent_id in set(tool.agent_id for tool in self.tool_metrics):
            agent_tools = [t for t in self.tool_metrics if t.agent_id == agent_id]
            
            profile = AgentProfile(agent_id=agent_id)
            profile.total_tools = len(agent_tools)
            
            if agent_tools:
                # Complexity metrics
                profile.avg_complexity = statistics.mean(t.tci_score for t in agent_tools)
                profile.complexity_trajectory = [t.tci_score for t in 
                                               sorted(agent_tools, key=lambda x: x.round_created)]
                
                # Specialization analysis
                categories = [t.semantic_category for t in agent_tools]
                category_counts = Counter(categories)
                if categories:
                    most_common_category, max_count = category_counts.most_common(1)[0]
                    profile.specialization_score = max_count / len(categories)
                    profile.tool_categories = list(category_counts.keys())
                
                # Innovation index (based on unique tool names and complexity)
                unique_patterns = len(set(t.name.lower() for t in agent_tools))
                profile.innovation_index = unique_patterns / len(agent_tools)
                
                # Consistency (variance in complexity)
                if len(agent_tools) > 1:
                    complexity_values = [t.tci_score for t in agent_tools if t.tci_score > 0]
                    if len(complexity_values) > 1:
                        complexity_variance = statistics.variance(complexity_values)
                        profile.consistency_score = 1.0 / (1.0 + complexity_variance)
                    else:
                        profile.consistency_score = 1.0
                else:
                    profile.consistency_score = 1.0
            
            # Load reflection data for strategic evolution analysis
            self._analyze_agent_reflections(agent_id, profile)
            
            self.agent_profiles[agent_id] = profile
    
    def _analyze_agent_reflections(self, agent_id: str, profile: AgentProfile):
        """Analyze agent reflection patterns for strategic evolution."""
        reflection_file = self.exp_dir / 'personal_tools' / agent_id / 'reflection_history.json'
        
        if reflection_file.exists():
            try:
                with open(reflection_file, 'r') as f:
                    reflection_data = json.load(f)
                
                profile.total_reflections = reflection_data.get('total_reflections', 0)
                
                # Analyze reflection content for strategic themes
                reflections = reflection_data.get('reflections', [])
                themes = []
                
                for reflection in reflections:
                    text = reflection.get('reflection', '').lower()
                    if 'alignment' in text or 'align' in text:
                        themes.append('alignment')
                    if 'separation' in text or 'unique' in text:
                        themes.append('separation')
                    if 'cohesion' in text or 'collective' in text:
                        themes.append('cohesion')
                    if 'innovation' in text or 'novel' in text:
                        themes.append('innovation')
                
                profile.strategic_evolution = themes
                
            except Exception as e:
                print(f"⚠️ Failed to analyze reflections for {agent_id}: {e}")
    
    def _analyze_ecosystem(self):
        """Analyze system-level emergent properties."""
        print("🌐 Analyzing ecosystem-level emergence...")
        
        if not self.tool_metrics:
            return
        
        metrics = self.ecosystem_metrics
        metrics.total_tools = len(self.tool_metrics)
        
        # Functional diversity (normalized Shannon entropy of tool categories)
        categories = [t.semantic_category for t in self.tool_metrics]
        category_counts = Counter(categories)
        total = len(categories)
        
        if total > 0:
            entropy = -sum((count/total) * math.log2(count/total) 
                          for count in category_counts.values() if count > 0)
            max_entropy = math.log2(len(category_counts)) if len(category_counts) > 1 else 1
            metrics.category_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Redundancy analysis (duplicate names)
        tool_names = [t.name.lower().strip() for t in self.tool_metrics]
        name_counts = Counter(tool_names)
        duplicates = sum(count - 1 for count in name_counts.values() if count > 1)
        metrics.redundancy_rate = duplicates / len(tool_names) if tool_names else 0
        
        # Modularity index (inverse coefficient of variation of LOC)
        loc_values = [t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0]
        if loc_values:
            loc_variance = statistics.variance(loc_values)
            loc_mean = statistics.mean(loc_values)
            metrics.loc_consistency = 1.0 / (1.0 + (loc_variance / loc_mean)) if loc_mean > 0 else 0
        
        # Innovation rate (tools with unique semantic fingerprints)
        semantic_fingerprints = set()
        for tool in self.tool_metrics:
            fingerprint = f"{tool.semantic_category}_{tool.parameter_count}_{tool.function_count}"
            semantic_fingerprints.add(fingerprint)
        
        metrics.unique_pattern_ratio = len(semantic_fingerprints) / len(self.tool_metrics) if self.tool_metrics else 0
        
        # Complexity coherence (consistency across agents)
        agent_complexities = {}
        for tool in self.tool_metrics:
            if tool.agent_id not in agent_complexities:
                agent_complexities[tool.agent_id] = []
            agent_complexities[tool.agent_id].append(tool.tci_score)
        
        if len(agent_complexities) > 1:
            agent_avg_complexities = [statistics.mean(complexities) 
                                    for complexities in agent_complexities.values() if complexities]
            if len(agent_avg_complexities) > 1:
                complexity_variance = statistics.variance(agent_avg_complexities)
                metrics.agent_complexity_variance = 1.0 / (1.0 + complexity_variance)
            else:
                metrics.agent_complexity_variance = 1.0
        else:
            metrics.agent_complexity_variance = 1.0
        
        # Emergent specialization (concentration of agents in dominant categories)
        agent_categories = {}
        for tool in self.tool_metrics:
            if tool.agent_id not in agent_categories:
                agent_categories[tool.agent_id] = []
            agent_categories[tool.agent_id].append(tool.semantic_category)
        
        specialization_scores = []
        for agent_id, categories in agent_categories.items():
            if categories:
                category_counts = Counter(categories)
                max_count = max(category_counts.values())
                specialization = max_count / len(categories)
                specialization_scores.append(specialization)
        
        metrics.category_concentration = statistics.mean(specialization_scores) if specialization_scores else 0
        
        # Adaptive learning (based on center history evolution)
        if self.center_history and len(self.center_history) > 1:
            # Measure semantic similarity between consecutive center descriptions
            similarities = []
            for i in range(1, len(self.center_history)):
                prev_words = set(re.findall(r'\b\w+\b', self.center_history[i-1].lower()))
                curr_words = set(re.findall(r'\b\w+\b', self.center_history[i].lower()))
                
                if prev_words and curr_words:
                    similarity = len(prev_words & curr_words) / len(prev_words | curr_words)
                    similarities.append(similarity)
            
            if similarities:
                # Adaptive learning is higher when there's moderate change (not too static, not too chaotic)
                avg_similarity = statistics.mean(similarities)
                metrics.center_drift_rate = 1.0 - abs(avg_similarity - 0.5) * 2
    
    def _analyze_temporal_patterns(self):
        """Analyze how metrics evolve over rounds."""
        print("⏰ Analyzing temporal patterns...")
        
        # Group tools by round
        rounds = defaultdict(list)
        for tool in self.tool_metrics:
            rounds[tool.round_created].append(tool)
        
        # Calculate round-by-round metrics
        for round_num in sorted(rounds.keys()):
            round_tools = rounds[round_num]
            
            self.temporal_data['round'].append(round_num)
            self.temporal_data['tools_created'].append(len(round_tools))
            self.temporal_data['avg_complexity'].append(
                statistics.mean(t.tci_score for t in round_tools) if round_tools else 0
            )
            self.temporal_data['avg_loc'].append(
                statistics.mean(t.lines_of_code for t in round_tools) if round_tools else 0
            )
            
            # Diversity in this round
            categories = [t.semantic_category for t in round_tools]
            unique_categories = len(set(categories))
            self.temporal_data['category_diversity'].append(unique_categories)
            
            # Innovation (new categories introduced)
            if round_num == 1:
                self.temporal_data['innovation_count'].append(unique_categories)
            else:
                prev_categories = set()
                for prev_round in range(1, round_num):
                    prev_tools = rounds.get(prev_round, [])
                    prev_categories.update(t.semantic_category for t in prev_tools)
                
                new_categories = set(categories) - prev_categories
                self.temporal_data['innovation_count'].append(len(new_categories))
    
    def _create_complexity_visualizations(self):
        """Create comprehensive complexity visualizations following TCI design."""
        print("📈 Creating complexity visualizations...")
        
        output_dir = self.exp_dir / 'analysis_results'
        output_dir.mkdir(exist_ok=True)
        
        # 1. TCI Evolution Over Rounds (Main complexity plot)
        self._plot_tci_evolution(output_dir)
        
        # 2. Complexity Component Breakdown
        self._plot_complexity_breakdown(output_dir)
        
        # 3. Agent Complexity Profiles
        self._plot_agent_complexity_profiles(output_dir)
        
        # 4. Complexity Distribution Analysis
        self._plot_complexity_distributions(output_dir)
    
    def _plot_tci_evolution(self, output_dir: Path):
        """Plot TCI evolution over rounds (main complexity visualization)."""
        if not self.temporal_data['round']:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Main TCI evolution line
        plt.subplot(2, 2, 1)
        plt.plot(self.temporal_data['round'], self.temporal_data['avg_complexity'], 
                'bo-', linewidth=2, markersize=6, label='Average TCI')
        plt.xlabel('Round')
        plt.ylabel('Average TCI Score')
        plt.title('TCI Evolution Over Time')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Tools created per round
        plt.subplot(2, 2, 2)
        plt.bar(self.temporal_data['round'], self.temporal_data['tools_created'], 
                alpha=0.7, color='green')
        plt.xlabel('Round')
        plt.ylabel('Tools Created')
        plt.title('Tool Creation Rate')
        plt.grid(True, alpha=0.3)
        
        # Category diversity
        plt.subplot(2, 2, 3)
        plt.plot(self.temporal_data['round'], self.temporal_data['category_diversity'], 
                'ro-', linewidth=2, markersize=6)
        plt.xlabel('Round')
        plt.ylabel('Unique Categories')
        plt.title('Category Entropy Evolution')
        plt.grid(True, alpha=0.3)
        
        # Innovation rate
        plt.subplot(2, 2, 4)
        plt.bar(self.temporal_data['round'], self.temporal_data['innovation_count'], 
                alpha=0.7, color='orange')
        plt.xlabel('Round')
        plt.ylabel('New Categories Introduced')
        plt.title('Unique Pattern Ratio')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'tci_evolution_comprehensive.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_complexity_breakdown(self, output_dir: Path):
        """Plot complexity component breakdown."""
        if not self.tool_metrics:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Component contributions
        code_comp = [t.code_complexity for t in self.tool_metrics]
        interface_comp = [t.interface_complexity for t in self.tool_metrics]
        compositional_comp = [t.compositional_complexity for t in self.tool_metrics]
        
        # Stacked area chart of complexity components over rounds
        rounds_data = defaultdict(lambda: {'code': [], 'interface': [], 'compositional': []})
        for tool in self.tool_metrics:
            rounds_data[tool.round_created]['code'].append(tool.code_complexity)
            rounds_data[tool.round_created]['interface'].append(tool.interface_complexity)
            rounds_data[tool.round_created]['compositional'].append(tool.compositional_complexity)
        
        rounds = sorted(rounds_data.keys())
        code_avgs = [statistics.mean(rounds_data[r]['code']) if rounds_data[r]['code'] else 0 for r in rounds]
        interface_avgs = [statistics.mean(rounds_data[r]['interface']) if rounds_data[r]['interface'] else 0 for r in rounds]
        comp_avgs = [statistics.mean(rounds_data[r]['compositional']) if rounds_data[r]['compositional'] else 0 for r in rounds]
        
        axes[0,0].stackplot(rounds, code_avgs, interface_avgs, comp_avgs, 
                           labels=['Code', 'Interface', 'Compositional'],
                           alpha=0.7, colors=['#ff9999', '#66b3ff', '#99ff99'])
        axes[0,0].set_xlabel('Round')
        axes[0,0].set_ylabel('Average Complexity')
        axes[0,0].set_title('Complexity Components Over Time')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Complexity distribution by component
        components = ['Code', 'Interface', 'Compositional']
        component_data = [code_comp, interface_comp, compositional_comp]
        
        axes[0,1].boxplot(component_data, labels=components)
        axes[0,1].set_ylabel('Complexity Score')
        axes[0,1].set_title('Complexity Component Distributions')
        axes[0,1].grid(True, alpha=0.3)
        
        # Agent complexity heatmap
        agent_complexity_matrix = []
        agent_ids = sorted(set(t.agent_id for t in self.tool_metrics))
        
        max_rounds = max(rounds) if rounds else 1
        for agent_id in agent_ids:
            agent_tools = [t for t in self.tool_metrics if t.agent_id == agent_id]
            agent_rounds = [0] * max_rounds
            
            for tool in agent_tools:
                if tool.round_created <= len(agent_rounds):
                    agent_rounds[tool.round_created - 1] = tool.tci_score
            
            agent_complexity_matrix.append(agent_rounds)
        
        if agent_complexity_matrix:
            im = axes[1,0].imshow(agent_complexity_matrix, aspect='auto', cmap='viridis')
            axes[1,0].set_xlabel('Round')
            axes[1,0].set_ylabel('Agent')
            axes[1,0].set_title('Agent Complexity Heatmap')
            axes[1,0].set_yticks(range(len(agent_ids)))
            axes[1,0].set_yticklabels(agent_ids)
            plt.colorbar(im, ax=axes[1,0])
        
        # Tool complexity vs LOC scatter
        loc_values = [t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0]
        tci_values = [t.tci_score for t in self.tool_metrics if t.lines_of_code > 0]
        
        if loc_values and tci_values:
            axes[1,1].scatter(loc_values, tci_values, alpha=0.6, s=50)
            axes[1,1].set_xlabel('Lines of Code')
            axes[1,1].set_ylabel('TCI Score')
            axes[1,1].set_title('Complexity vs Size')
            axes[1,1].grid(True, alpha=0.3)
            
            # Add trend line
            if len(loc_values) > 1:
                z = np.polyfit(loc_values, tci_values, 1)
                p = np.poly1d(z)
                axes[1,1].plot(sorted(loc_values), p(sorted(loc_values)), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'complexity_breakdown_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_agent_complexity_profiles(self, output_dir: Path):
        """Plot individual agent complexity profiles and trajectories."""
        if not self.agent_profiles:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Agent complexity trajectories
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        for i, (agent_id, profile) in enumerate(self.agent_profiles.items()):
            if profile.complexity_trajectory:
                rounds = list(range(1, len(profile.complexity_trajectory) + 1))
                color = colors[i % len(colors)]
                axes[0,0].plot(rounds, profile.complexity_trajectory, 
                              'o-', label=agent_id, linewidth=2, markersize=4, color=color)
        
        axes[0,0].set_xlabel('Round')
        axes[0,0].set_ylabel('TCI Score')
        axes[0,0].set_title('Agent Complexity Trajectories')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Agent specialization scores
        agent_names = list(self.agent_profiles.keys())
        specialization_scores = [profile.specialization_score for profile in self.agent_profiles.values()]
        
        axes[0,1].bar(agent_names, specialization_scores, alpha=0.7, color='skyblue')
        axes[0,1].set_xlabel('Agent')
        axes[0,1].set_ylabel('Specialization Score')
        axes[0,1].set_title('Agent Specialization Levels')
        axes[0,1].grid(True, alpha=0.3)
        plt.setp(axes[0,1].get_xticklabels(), rotation=45)
        
        # Innovation vs Consistency scatter
        innovation_scores = [profile.innovation_index for profile in self.agent_profiles.values()]
        consistency_scores = [profile.consistency_score for profile in self.agent_profiles.values()]
        
        axes[1,0].scatter(innovation_scores, consistency_scores, s=100, alpha=0.7)
        for i, agent_id in enumerate(agent_names):
            axes[1,0].annotate(agent_id, (innovation_scores[i], consistency_scores[i]), 
                              xytext=(5, 5), textcoords='offset points')
        axes[1,0].set_xlabel('Innovation Index')
        axes[1,0].set_ylabel('Consistency Score')
        axes[1,0].set_title('Innovation vs Consistency')
        axes[1,0].grid(True, alpha=0.3)
        
        # Agent tool category distribution
        all_categories = set()
        for profile in self.agent_profiles.values():
            all_categories.update(profile.tool_categories)
        
        if all_categories:
            category_matrix = []
            for agent_id in agent_names:
                agent_categories = self.agent_profiles[agent_id].tool_categories
                category_counts = Counter(agent_categories)
                row = [category_counts.get(cat, 0) for cat in sorted(all_categories)]
                category_matrix.append(row)
            
            if category_matrix:
                im = axes[1,1].imshow(category_matrix, aspect='auto', cmap='Blues')
                axes[1,1].set_xlabel('Tool Category')
                axes[1,1].set_ylabel('Agent')
                axes[1,1].set_title('Agent-Category Distribution')
                axes[1,1].set_yticks(range(len(agent_names)))
                axes[1,1].set_yticklabels(agent_names)
                axes[1,1].set_xticks(range(len(all_categories)))
                axes[1,1].set_xticklabels(sorted(all_categories), rotation=45, ha='right')
                plt.colorbar(im, ax=axes[1,1])
        
        plt.tight_layout()
        plt.savefig(output_dir / 'agent_complexity_profiles.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_complexity_distributions(self, output_dir: Path):
        """Plot complexity distribution analysis."""
        if not self.tool_metrics:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        
        # TCI score distribution
        tci_scores = [t.tci_score for t in self.tool_metrics if t.tci_score > 0]
        if tci_scores:
            axes[0,0].hist(tci_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0,0].axvline(statistics.mean(tci_scores), color='red', linestyle='--', 
                             label=f'Mean: {statistics.mean(tci_scores):.2f}')
            axes[0,0].set_xlabel('TCI Score')
            axes[0,0].set_ylabel('Frequency')
            axes[0,0].set_title('TCI Score Distribution')
            axes[0,0].legend()
            axes[0,0].grid(True, alpha=0.3)
        
        # Lines of code distribution
        loc_values = [t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0]
        if loc_values:
            axes[0,1].hist(loc_values, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
            axes[0,1].axvline(statistics.mean(loc_values), color='red', linestyle='--',
                             label=f'Mean: {statistics.mean(loc_values):.1f}')
            axes[0,1].set_xlabel('Lines of Code')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title('Tool Size Distribution')
            axes[0,1].legend()
            axes[0,1].grid(True, alpha=0.3)
        
        # Function count distribution
        func_counts = [t.function_count for t in self.tool_metrics if t.function_count > 0]
        if func_counts:
            axes[0,2].hist(func_counts, bins=max(10, max(func_counts)), alpha=0.7, 
                          color='orange', edgecolor='black')
            axes[0,2].set_xlabel('Function Count')
            axes[0,2].set_ylabel('Frequency')
            axes[0,2].set_title('Function Count Distribution')
            axes[0,2].grid(True, alpha=0.3)
        
        # Category distribution pie chart
        categories = [t.semantic_category for t in self.tool_metrics]
        category_counts = Counter(categories)
        
        if category_counts:
            axes[1,0].pie(category_counts.values(), labels=category_counts.keys(), 
                         autopct='%1.1f%%', startangle=90)
            axes[1,0].set_title('Tool Category Distribution')
        
        # Complexity by category boxplot
        category_complexity = defaultdict(list)
        for tool in self.tool_metrics:
            if tool.tci_score > 0:
                category_complexity[tool.semantic_category].append(tool.tci_score)
        
        if category_complexity:
            categories = list(category_complexity.keys())
            complexity_data = [category_complexity[cat] for cat in categories]
            
            axes[1,1].boxplot(complexity_data, labels=categories)
            axes[1,1].set_xlabel('Category')
            axes[1,1].set_ylabel('TCI Score')
            axes[1,1].set_title('Complexity by Category')
            axes[1,1].grid(True, alpha=0.3)
            plt.setp(axes[1,1].get_xticklabels(), rotation=45)
        
        # Test success rate by complexity
        test_passed = [t for t in self.tool_metrics if t.test_passed]
        test_failed = [t for t in self.tool_metrics if not t.test_passed]
        
        if test_passed and test_failed:
            passed_complexity = [t.tci_score for t in test_passed if t.tci_score > 0]
            failed_complexity = [t.tci_score for t in test_failed if t.tci_score > 0]
            
            axes[1,2].hist([passed_complexity, failed_complexity], 
                          bins=15, alpha=0.7, label=['Passed', 'Failed'], 
                          color=['green', 'red'], edgecolor='black')
            axes[1,2].set_xlabel('TCI Score')
            axes[1,2].set_ylabel('Frequency')
            axes[1,2].set_title('Test Success vs Complexity')
            axes[1,2].legend()
            axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'complexity_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_ecosystem_visualizations(self):
        """Create ecosystem-level visualizations."""
        print("🌐 Creating ecosystem visualizations...")
        
        output_dir = self.exp_dir / 'analysis_results'
        output_dir.mkdir(exist_ok=True)
        
        # Tool network graph
        self._create_tool_network(output_dir)
        
        # Emergent intelligence dashboard
        self._create_intelligence_dashboard(output_dir)
    
    def _create_tool_network(self, output_dir: Path):
        """Create tool ecosystem network visualization."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create a simple network based on semantic similarity
        categories = list(set(t.semantic_category for t in self.tool_metrics))
        category_positions = {}
        
        # Arrange categories in a circle
        for i, category in enumerate(categories):
            angle = 2 * math.pi * i / len(categories)
            x = math.cos(angle) * 3
            y = math.sin(angle) * 3
            category_positions[category] = (x, y)
        
        # Plot tools as nodes
        agent_colors = {'Agent_01': 'red', 'Agent_02': 'blue', 'Agent_03': 'green', 
                       'Agent_04': 'orange', 'Agent_05': 'purple'}
        
        for tool in self.tool_metrics:
            if tool.semantic_category in category_positions:
                x, y = category_positions[tool.semantic_category]
                # Add some jitter
                x += np.random.normal(0, 0.3)
                y += np.random.normal(0, 0.3)
                
                # Size based on complexity, color based on agent
                size = max(50, tool.tci_score * 100)
                color = agent_colors.get(tool.agent_id, 'gray')
                
                ax.scatter(x, y, s=size, c=color, alpha=0.6, edgecolors='black')
        
        # Add category labels
        for category, (x, y) in category_positions.items():
            ax.text(x, y, category, fontsize=10, ha='center', va='center', 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        ax.set_title('Tool Ecosystem Network')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Create legend for agents
        legend_elements = [plt.scatter([], [], c=color, s=100, label=agent) 
                          for agent, color in agent_colors.items() if agent in [t.agent_id for t in self.tool_metrics]]
        ax.legend(handles=legend_elements, title='Agents')
        
        plt.savefig(output_dir / 'tool_ecosystem_network.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_intelligence_dashboard(self, output_dir: Path):
        """Create emergent intelligence metrics dashboard."""
        metrics = self.ecosystem_metrics
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        
        # Radar chart for ecosystem metrics
        categories = ['Functional\nDiversity', 'Modularity\nIndex', 'Innovation\nRate', 
                     'Complexity\nCoherence', 'Emergent\nSpecialization', 'Adaptive\nLearning']
        values = [metrics.category_entropy, metrics.loc_consistency, metrics.unique_pattern_ratio,
                 metrics.agent_complexity_variance, metrics.category_concentration, metrics.center_drift_rate]
        
        # Normalize values to 0-1 range for radar chart
        normalized_values = [max(0, min(1, v)) for v in values]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Complete the circle
        normalized_values = normalized_values + [normalized_values[0]]  # Complete the circle
        
        ax_radar = plt.subplot(2, 3, 1, projection='polar')
        ax_radar.plot(angles, normalized_values, 'o-', linewidth=2, color='blue', alpha=0.7)
        ax_radar.fill(angles, normalized_values, alpha=0.25, color='blue')
        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(categories)
        ax_radar.set_ylim(0, 1)
        ax_radar.set_title('Emergent Intelligence Metrics', pad=20)
        ax_radar.grid(True)
        
        # Redundancy analysis
        tool_names = [t.name.lower().strip() for t in self.tool_metrics]
        name_counts = Counter(tool_names)
        unique_names = len([name for name, count in name_counts.items() if count == 1])
        duplicate_names = len(tool_names) - unique_names
        
        axes[0,1].pie([unique_names, duplicate_names], labels=['Unique', 'Duplicate'], 
                     autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        axes[0,1].set_title(f'Tool Name Redundancy\n(Rate: {metrics.redundancy_rate:.2f})')
        
        # Innovation timeline
        if self.temporal_data['round']:
            cumulative_innovation = np.cumsum(self.temporal_data['innovation_count'])
            axes[0,2].plot(self.temporal_data['round'], cumulative_innovation, 'go-', linewidth=2)
            axes[0,2].set_xlabel('Round')
            axes[0,2].set_ylabel('Cumulative New Categories')
            axes[0,2].set_title('Innovation Accumulation')
            axes[0,2].grid(True, alpha=0.3)
        
        # Test success metrics
        total_tools = len(self.tool_metrics)
        if total_tools > 0:
            passed_tests = len([t for t in self.tool_metrics if t.test_passed])
            failed_tests = total_tools - passed_tests
            
            axes[1,0].bar(['Passed', 'Failed'], [passed_tests, failed_tests], 
                         color=['green', 'red'], alpha=0.7)
            axes[1,0].set_ylabel('Number of Tools')
            axes[1,0].set_title(f'Test Success Rate: {passed_tests/total_tools*100:.1f}%')
            axes[1,0].grid(True, alpha=0.3)
        
        # Complexity evolution trend
        if len(self.temporal_data['avg_complexity']) > 1:
            x = np.array(self.temporal_data['round'])
            y = np.array(self.temporal_data['avg_complexity'])
            
            # Fit trend line
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            axes[1,1].plot(x, y, 'bo-', label='Actual', linewidth=2)
            axes[1,1].plot(x, p(x), 'r--', label=f'Trend (slope: {z[0]:.3f})', linewidth=2)
            axes[1,1].set_xlabel('Round')
            axes[1,1].set_ylabel('Average TCI')
            axes[1,1].set_title('Complexity Evolution Trend')
            axes[1,1].legend()
            axes[1,1].grid(True, alpha=0.3)
        
        # Agent productivity comparison
        agent_productivity = {}
        for tool in self.tool_metrics:
            if tool.agent_id not in agent_productivity:
                agent_productivity[tool.agent_id] = 0
            agent_productivity[tool.agent_id] += 1
        
        if agent_productivity:
            agents = list(agent_productivity.keys())
            productivity = list(agent_productivity.values())
            
            axes[1,2].bar(agents, productivity, alpha=0.7, color='skyblue')
            axes[1,2].set_xlabel('Agent')
            axes[1,2].set_ylabel('Tools Created')
            axes[1,2].set_title('Agent Productivity')
            axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'emergent_intelligence_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_agent_analysis(self):
        """Create detailed agent behavior analysis."""
        print("🤖 Creating agent analysis...")
        
        output_dir = self.exp_dir / 'analysis_results'
        output_dir.mkdir(exist_ok=True)
        
        # Agent strategic evolution wordcloud
        self._create_strategy_wordcloud(output_dir)
        
        # Agent collaboration matrix
        self._create_collaboration_analysis(output_dir)
    
    def _create_strategy_wordcloud(self, output_dir: Path):
        """Create word cloud from agent reflections."""
        if not WORDCLOUD_AVAILABLE:
            print("⚠️ Skipping wordcloud - library not available")
            return
            
        all_reflections = []
        
        for agent_id in self.agent_profiles.keys():
            reflection_file = self.exp_dir / 'personal_tools' / agent_id / 'reflection_history.json'
            
            if reflection_file.exists():
                try:
                    with open(reflection_file, 'r') as f:
                        data = json.load(f)
                    
                    for reflection in data.get('reflections', []):
                        text = reflection.get('reflection', '')
                        all_reflections.append(text)
                        
                except Exception:
                    continue
        
        if all_reflections:
            combined_text = ' '.join(all_reflections)
            
            # Clean text for word cloud
            cleaned_text = re.sub(r'[^\w\s]', ' ', combined_text.lower())
            
            # Create word cloud
            wordcloud = WordCloud(width=800, height=400, background_color='white',
                                 max_words=100, colormap='viridis').generate(cleaned_text)
            
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Agent Strategic Thinking Patterns', fontsize=16)
            plt.savefig(output_dir / 'agent_strategy_wordcloud.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_collaboration_analysis(self, output_dir: Path):
        """Analyze collaboration patterns between agents."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Agent similarity matrix based on tool categories
        agents = list(self.agent_profiles.keys())
        similarity_matrix = np.zeros((len(agents), len(agents)))
        
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    categories1 = set(self.agent_profiles[agent1].tool_categories)
                    categories2 = set(self.agent_profiles[agent2].tool_categories)
                    
                    if categories1 and categories2:
                        similarity = len(categories1 & categories2) / len(categories1 | categories2)
                        similarity_matrix[i][j] = similarity
        
        im = axes[0].imshow(similarity_matrix, cmap='Blues')
        axes[0].set_xticks(range(len(agents)))
        axes[0].set_yticks(range(len(agents)))
        axes[0].set_xticklabels(agents)
        axes[0].set_yticklabels(agents)
        axes[0].set_title('Agent Similarity Matrix\n(Based on Tool Categories)')
        
        # Add text annotations
        for i in range(len(agents)):
            for j in range(len(agents)):
                text = axes[0].text(j, i, f'{similarity_matrix[i, j]:.2f}',
                                   ha="center", va="center", color="black")
        
        plt.colorbar(im, ax=axes[0])
        
        # Agent complementarity analysis
        agent_specializations = []
        for agent_id in agents:
            profile = self.agent_profiles[agent_id]
            if profile.tool_categories:
                most_common = Counter(profile.tool_categories).most_common(1)[0][0]
                agent_specializations.append(most_common)
            else:
                agent_specializations.append('none')
        
        specialization_counts = Counter(agent_specializations)
        
        axes[1].pie(specialization_counts.values(), labels=specialization_counts.keys(),
                   autopct='%1.1f%%', startangle=90)
        axes[1].set_title('Agent Primary Specializations')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'collaboration_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        print("📄 Generating comprehensive report...")
        
        output_dir = self.exp_dir / 'analysis_results'
        output_dir.mkdir(exist_ok=True)
        
        # Calculate key metrics
        avg_complexity = statistics.mean(t.tci_score for t in self.tool_metrics) if self.tool_metrics else 0
        avg_loc = statistics.mean(t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0) if self.tool_metrics else 0
        test_pass_rate = len([t for t in self.tool_metrics if t.test_passed]) / len(self.tool_metrics) if self.tool_metrics else 0
        median_loc = statistics.median([t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0]) if self.tool_metrics else 0
        p75_loc = np.percentile([t.lines_of_code for t in self.tool_metrics if t.lines_of_code > 0], 75) if self.tool_metrics else 0
        
        # Compile all metrics
        report = {
            'experiment_metadata': {
                'name': self.metadata.get('name', 'Unknown'),
                'agents': self.metadata.get('num_agents', 0),
                'rounds': self.metadata.get('max_rounds', 0),
                'boids_enabled': self.metadata.get('boids_enabled', False),
                'timestamp': self.metadata.get('timestamp', ''),
            },
            'tool_metrics_summary': {
                'total_tools': len(self.tool_metrics),
                'avg_complexity': avg_complexity,
                'avg_loc': avg_loc,
                'test_pass_rate': test_pass_rate,
                'category_diversity': len(set(t.semantic_category for t in self.tool_metrics)),
                'median_loc': median_loc,
                'p75_loc': p75_loc,
                'duplicate_name_rate': self.ecosystem_metrics.redundancy_rate,
            },
            'agent_profiles': {
                agent_id: {
                    'total_tools': profile.total_tools,
                    'avg_complexity': profile.avg_complexity,
                    'specialization_score': profile.specialization_score,
                    'innovation_index': profile.innovation_index,
                    'consistency_score': profile.consistency_score,
                    'primary_categories': profile.tool_categories[:3],
                }
                for agent_id, profile in self.agent_profiles.items()
            },
            'ecosystem_intelligence': {
                'category_entropy': self.ecosystem_metrics.category_entropy,
                'loc_consistency': self.ecosystem_metrics.loc_consistency,
                'redundancy_rate': self.ecosystem_metrics.redundancy_rate,
                'unique_pattern_ratio': self.ecosystem_metrics.unique_pattern_ratio,
                'agent_complexity_variance': self.ecosystem_metrics.agent_complexity_variance,
                'category_concentration': self.ecosystem_metrics.category_concentration,
                'center_drift_rate': self.ecosystem_metrics.center_drift_rate,
            },
            'temporal_patterns': {
                'complexity_trend': {
                    'rounds': self.temporal_data['round'],
                    'avg_complexity': self.temporal_data['avg_complexity'],
                    'trend_slope': np.polyfit(self.temporal_data['round'], self.temporal_data['avg_complexity'], 1)[0] if len(self.temporal_data['round']) > 1 else 0,
                },
                'innovation_pattern': {
                    'rounds': self.temporal_data['round'],
                    'new_categories': self.temporal_data['innovation_count'],
                    'cumulative_categories': np.cumsum(self.temporal_data['innovation_count']).tolist() if self.temporal_data['innovation_count'] else [],
                },
            },
            'emergent_intelligence_indicators': {
                'coordination_evidence': self.ecosystem_metrics.category_concentration > 0.6,
                'adaptive_learning': self.ecosystem_metrics.center_drift_rate > 0.5,
                'collective_innovation': self.ecosystem_metrics.unique_pattern_ratio > 0.7,
                'system_coherence': self.ecosystem_metrics.agent_complexity_variance > 0.6,
                'functional_emergence': self.ecosystem_metrics.category_entropy > 0.8,
            }
        }
        
        # Save report as JSON
        with open(output_dir / 'comprehensive_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate markdown summary
        self._generate_markdown_summary(report, output_dir)
        
        return report
    
    def _generate_markdown_summary(self, report: Dict[str, Any], output_dir: Path):
        """Generate markdown summary report."""
        md_content = f"""# Experiment Analysis Report

## Experiment Overview
- **Name**: {report['experiment_metadata']['name']}
- **Agents**: {report['experiment_metadata']['agents']}
- **Rounds**: {report['experiment_metadata']['rounds']}
- **Boids Enabled**: {report['experiment_metadata']['boids_enabled']}
- **Timestamp**: {report['experiment_metadata']['timestamp']}

## Tool Ecosystem Metrics
- **Total Tools Created**: {report['tool_metrics_summary']['total_tools']}
- **Average TCI Complexity**: {report['tool_metrics_summary']['avg_complexity']:.3f}
- **Average Lines of Code**: {report['tool_metrics_summary']['avg_loc']:.1f}
- **Median LOC**: {report['tool_metrics_summary']['median_loc']:.1f}
- **75th Percentile LOC**: {report['tool_metrics_summary']['p75_loc']:.1f}
- **Test Pass Rate**: {report['tool_metrics_summary']['test_pass_rate']:.1%}
- **Category Entropy**: {report['tool_metrics_summary']['category_diversity']} categories
- **Duplicate Name Rate**: {report['tool_metrics_summary']['duplicate_name_rate']:.3f}

## Agent Performance Profiles
"""
        
        for agent_id, profile in report['agent_profiles'].items():
            md_content += f"""
### {agent_id}
- **Tools Created**: {profile['total_tools']}
- **Average Complexity**: {profile['avg_complexity']:.3f}
- **Specialization Score**: {profile['specialization_score']:.3f}
- **Innovation Index**: {profile['innovation_index']:.3f}
- **Consistency Score**: {profile['consistency_score']:.3f}
- **Primary Categories**: {', '.join(profile['primary_categories'])}
"""
        
        md_content += f"""
## Emergent Intelligence Metrics
- **Category Entropy**: {report['ecosystem_intelligence']['category_entropy']:.3f}
- **LOC Consistency**: {report['ecosystem_intelligence']['loc_consistency']:.3f}
- **Unique Pattern Ratio**: {report['ecosystem_intelligence']['unique_pattern_ratio']:.3f}
- **Complexity Coherence**: {report['ecosystem_intelligence']['agent_complexity_variance']:.3f}
- **Category Concentration**: {report['ecosystem_intelligence']['category_concentration']:.3f}
- **Center Drift Score**: {report['ecosystem_intelligence']['center_drift_rate']:.3f}

## Emergent Intelligence Indicators
- **Category Concentration**: {'✅ YES' if report['emergent_intelligence_indicators']['coordination_evidence'] else '❌ NO'}
- **Center Drift**: {'✅ YES' if report['emergent_intelligence_indicators']['adaptive_learning'] else '❌ NO'}
- **Pattern Uniqueness**: {'✅ YES' if report['emergent_intelligence_indicators']['collective_innovation'] else '❌ NO'}
- **Agent Complexity Variance**: {'✅ YES' if report['emergent_intelligence_indicators']['system_coherence'] else '❌ NO'}
- **Functional Emergence**: {'✅ YES' if report['emergent_intelligence_indicators']['functional_emergence'] else '❌ NO'}

## Temporal Analysis
- **Complexity Trend Slope**: {report['temporal_patterns']['complexity_trend']['trend_slope']:.4f}
- **Total Innovation Events**: {sum(report['temporal_patterns']['innovation_pattern']['new_categories'])}
- **Final Category Count**: {max(report['temporal_patterns']['innovation_pattern']['cumulative_categories']) if report['temporal_patterns']['innovation_pattern']['cumulative_categories'] else 0}

## Visualizations Generated
1. `tci_evolution_comprehensive.png` - TCI evolution over time
2. `complexity_breakdown_analysis.png` - Complexity component analysis  
3. `agent_complexity_profiles.png` - Individual agent trajectories
4. `complexity_distributions.png` - Statistical distributions
5. `tool_ecosystem_network.png` - Tool relationship network
6. `emergent_intelligence_dashboard.png` - System-level metrics
7. `agent_strategy_wordcloud.png` - Strategic thinking patterns
8. `collaboration_analysis.png` - Agent collaboration patterns

---
*Generated by ExperimentAnalyzer - Comprehensive Analysis for Emergent Intelligence Research*
"""
        
        with open(output_dir / 'analysis_summary.md', 'w') as f:
            f.write(md_content)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Experiment Result Analyzer')
    parser.add_argument('experiment_dir', help='Path to experiment directory')
    parser.add_argument('--output-format', choices=['json', 'csv', 'both'], default='both',
                       help='Output format for results')
    
    args = parser.parse_args()
    
    if not Path(args.experiment_dir).exists():
        print(f"❌ Experiment directory not found: {args.experiment_dir}")
        return 1
    
    try:
        analyzer = ExperimentAnalyzer(args.experiment_dir)
        report = analyzer.analyze_experiment()
        
        print(f"\n🎉 Analysis Complete!")
        print(f"📊 Total Tools Analyzed: {report['tool_metrics_summary']['total_tools']}")
        print(f"🧠 Center Drift Rate: {report['ecosystem_intelligence']['center_drift_rate']:.3f}")
        print(f"📈 Unique Pattern Ratio: {report['ecosystem_intelligence']['unique_pattern_ratio']:.3f}")
        print(f"🔗 Agent Complexity Variance: {report['ecosystem_intelligence']['agent_complexity_variance']:.3f}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
