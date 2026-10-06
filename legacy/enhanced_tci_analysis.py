#!/usr/bin/env python3
"""
Enhanced TCI Analysis with Emergent Intelligence Metrics
========================================================

Comprehensive analysis comparing Boids vs Baseline experiments with:
1. Precise TCI metrics
2. Emergent intelligence indicators from experiment_result_analyzer.py
3. Test-case level pass rate (not tool-level)
"""

import json
import os
import glob
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns
import math
import statistics
from collections import Counter, defaultdict

def extract_comprehensive_data(experiment_path: str) -> Dict[str, Any]:
    """Extract comprehensive data including emergent intelligence metrics."""
    
    experiment_data = {
        'experiment_name': os.path.basename(experiment_path),
        'agents': {},
        'all_tci_scores': [],
        'all_tools': [],
        'rounds_data': {},
        'test_cases_data': [],  # NEW: Individual test case results
        'emergent_intelligence': {}
    }
    
    # Find all agent directories
    personal_tools_path = os.path.join(experiment_path, 'personal_tools')
    if not os.path.exists(personal_tools_path):
        return experiment_data
    
    agent_dirs = [d for d in os.listdir(personal_tools_path) 
                  if d.startswith('Agent_') and os.path.isdir(os.path.join(personal_tools_path, d))]
    
    total_test_cases = 0
    passed_test_cases = 0
    
    for agent_dir in sorted(agent_dirs):
        agent_path = os.path.join(personal_tools_path, agent_dir)
        index_file = os.path.join(agent_path, 'index.json')
        
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    agent_data = json.load(f)
                
                agent_info = {
                    'agent_id': agent_dir,
                    'tools': {},
                    'tci_scores': [],
                    'rounds': {},
                    'total_tools': 0,
                    'test_cases': []
                }
                
                for tool_name, tool_info in agent_data.get('tools', {}).items():
                    complexity = tool_info.get('complexity', {})
                    tci_score = complexity.get('tci_score', 0)
                    created_round = tool_info.get('created_in_round', 0)
                    test_passed = tool_info.get('test_passed', False)
                    
                    tool_data = {
                        'name': tool_name,
                        'tci_score': tci_score,
                        'code_complexity': complexity.get('code_complexity', 0),
                        'interface_complexity': complexity.get('interface_complexity', 0),
                        'compositional_complexity': complexity.get('compositional_complexity', 0),
                        'lines_of_code': complexity.get('lines_of_code', 0),
                        'param_count': complexity.get('param_count', 0),
                        'tool_calls': complexity.get('tool_calls', 0),
                        'external_imports': complexity.get('external_imports', 0),
                        'created_in_round': created_round,
                        'test_passed': test_passed,
                        'agent_id': agent_dir
                    }
                    
                    # Extract individual test case results
                    test_results_file = os.path.join(agent_path, '_testResults', f"{tool_name}_results.json")
                    if os.path.exists(test_results_file):
                        try:
                            with open(test_results_file, 'r') as f:
                                test_results = json.load(f)
                            
                            # Count individual test cases
                            passed_tests = test_results.get('passed_tests', 0)
                            failed_tests = test_results.get('failed_tests', 0)
                            total_tests = passed_tests + failed_tests
                            
                            if total_tests > 0:
                                test_case_data = {
                                    'tool_name': tool_name,
                                    'agent_id': agent_dir,
                                    'total_test_cases': total_tests,
                                    'passed_test_cases': passed_tests,
                                    'failed_test_cases': failed_tests,
                                    'pass_rate': passed_tests / total_tests,
                                    'tci_score': tci_score,
                                    'created_round': created_round
                                }
                                
                                agent_info['test_cases'].append(test_case_data)
                                experiment_data['test_cases_data'].append(test_case_data)
                                
                                total_test_cases += total_tests
                                passed_test_cases += passed_tests
                        except Exception as e:
                            print(f"⚠️ Failed to read test results for {tool_name}: {e}")
                    
                    agent_info['tools'][tool_name] = tool_data
                    agent_info['tci_scores'].append(tci_score)
                    agent_info['total_tools'] += 1
                    
                    # Group by rounds
                    if created_round not in agent_info['rounds']:
                        agent_info['rounds'][created_round] = []
                    agent_info['rounds'][created_round].append(tool_data)
                    
                    # Add to experiment-wide data
                    experiment_data['all_tci_scores'].append(tci_score)
                    experiment_data['all_tools'].append(tool_data)
                    
                    # Group by rounds for experiment
                    if created_round not in experiment_data['rounds_data']:
                        experiment_data['rounds_data'][created_round] = []
                    experiment_data['rounds_data'][created_round].append(tool_data)
                
                experiment_data['agents'][agent_dir] = agent_info
                
            except Exception as e:
                print(f"Error processing {agent_dir}: {e}")
    
    # Calculate test case level pass rate
    experiment_data['test_case_pass_rate'] = passed_test_cases / total_test_cases if total_test_cases > 0 else 0
    experiment_data['total_test_cases'] = total_test_cases
    experiment_data['passed_test_cases'] = passed_test_cases
    
    return experiment_data

def calculate_emergent_intelligence_metrics(experiment_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate emergent intelligence metrics similar to experiment_result_analyzer.py"""
    
    tools = experiment_data['all_tools']
    if not tools:
        return {}
    
    # 1. Category Entropy (Functional Diversity)
    categories = []
    for tool in tools:
        # Simple categorization based on tool name patterns
        name = tool['name'].lower()
        if any(word in name for word in ['pipeline', 'orchestrat', 'workflow']):
            categories.append('pipeline_orchestration')
        elif any(word in name for word in ['analysis', 'analyzer', 'pattern']):
            categories.append('data_analysis')
        elif any(word in name for word in ['risk', 'assessment', 'prediction']):
            categories.append('risk_assessment')
        elif any(word in name for word in ['scenario', 'simulation', 'model']):
            categories.append('scenario_modeling')
        elif any(word in name for word in ['ecological', 'conservation', 'environment']):
            categories.append('ecological_tools')
        else:
            categories.append('other')
    
    category_counts = Counter(categories)
    total = len(categories)
    
    if total > 0 and len(category_counts) > 1:
        entropy = -sum((count/total) * math.log2(count/total) 
                      for count in category_counts.values() if count > 0)
        max_entropy = math.log2(len(category_counts))
        category_entropy = entropy / max_entropy
    else:
        category_entropy = 0
    
    # 2. Modularity Q (Network Cohesion) - simplified version
    # Based on agent specialization in categories
    agent_categories = defaultdict(list)
    for tool in tools:
        agent_id = tool['agent_id']
        tool_category = categories[tools.index(tool)]  # Get corresponding category
        agent_categories[agent_id].append(tool_category)
    
    # Calculate agent category cohesion
    agent_cohesion_scores = []
    for agent_id, agent_cats in agent_categories.items():
        if len(agent_cats) > 1:
            unique_categories = len(set(agent_cats))
            cohesion = 1.0 - (unique_categories - 1) / len(agent_cats)
            agent_cohesion_scores.append(cohesion)
    
    modularity_q = statistics.mean(agent_cohesion_scores) if agent_cohesion_scores else 0.5
    
    # 3. Unique Pattern Ratio (Innovation)
    semantic_fingerprints = set()
    for tool in tools:
        fingerprint = f"{tool['param_count']}_{tool['tool_calls']}_{tool['external_imports']}"
        semantic_fingerprints.add(fingerprint)
    
    unique_pattern_ratio = len(semantic_fingerprints) / len(tools)
    
    # 4. Agent Complexity Variance (System Coherence)
    agent_complexities = defaultdict(list)
    for tool in tools:
        agent_complexities[tool['agent_id']].append(tool['tci_score'])
    
    if len(agent_complexities) > 1:
        agent_avg_complexities = [statistics.mean(complexities) 
                                for complexities in agent_complexities.values() if complexities]
        if len(agent_avg_complexities) > 1:
            complexity_variance = statistics.variance(agent_avg_complexities)
            agent_complexity_variance = 1.0 / (1.0 + complexity_variance)
        else:
            agent_complexity_variance = 1.0
    else:
        agent_complexity_variance = 1.0
    
    # 5. Specialization (NMI) - Normalized Mutual Information
    if len(agent_categories) > 1:
        all_agents = list(agent_categories.keys())
        all_categories = list(set(cat for cats in agent_categories.values() for cat in cats))
        
        if len(all_categories) > 0:
            # Simple specialization calculation
            specialization_scores = []
            for agent_id, agent_cats in agent_categories.items():
                if agent_cats:
                    category_counts = Counter(agent_cats)
                    max_count = max(category_counts.values())
                    specialization = max_count / len(agent_cats)
                    specialization_scores.append(specialization)
            
            category_concentration = statistics.mean(specialization_scores) if specialization_scores else 0
        else:
            category_concentration = 0
    else:
        category_concentration = 0
    
    # 6. Center Drift Rate (Adaptive Learning) - based on round evolution
    rounds_data = experiment_data['rounds_data']
    if len(rounds_data) > 1:
        round_complexities = []
        for round_num in sorted(rounds_data.keys()):
            round_tools = rounds_data[round_num]
            if round_tools:
                avg_complexity = statistics.mean(t['tci_score'] for t in round_tools)
                round_complexities.append(avg_complexity)
        
        if len(round_complexities) > 1:
            # Measure consistency of change (not too static, not too chaotic)
            changes = [abs(round_complexities[i] - round_complexities[i-1]) 
                      for i in range(1, len(round_complexities))]
            avg_change = statistics.mean(changes)
            # Normalize to 0-1 where moderate change = high adaptive learning
            center_drift_rate = min(1.0, avg_change / 2.0)  # Assuming max meaningful change is 2.0
        else:
            center_drift_rate = 0
    else:
        center_drift_rate = 0
    
    return {
        'category_entropy': category_entropy,
        'modularity_q': modularity_q,
        'unique_pattern_ratio': unique_pattern_ratio,
        'agent_complexity_variance': agent_complexity_variance,
        'category_concentration': category_concentration,
        'center_drift_rate': center_drift_rate
    }

def analyze_experiments_comprehensive():
    """Comprehensive analysis with emergent intelligence metrics."""
    
    # Experiment paths
    boids_path = "experiments/exp_boids_crocodile_conservation_intelligence_20250925_025019"
    baseline_path = "experiments/exp_global_crocodile_conservation_intelligence_20250925_024210"
    
    print("🔍 COMPREHENSIVE TCI + EMERGENT INTELLIGENCE ANALYSIS")
    print("=" * 80)
    
    # Extract data
    print("📊 Extracting comprehensive data from experiments...")
    boids_data = extract_comprehensive_data(boids_path)
    baseline_data = extract_comprehensive_data(baseline_path)
    
    print(f"✅ Boids: {len(boids_data['agents'])} agents, {len(boids_data['all_tools'])} tools, {boids_data['total_test_cases']} test cases")
    print(f"✅ Baseline: {len(baseline_data['agents'])} agents, {len(baseline_data['all_tools'])} tools, {baseline_data['total_test_cases']} test cases")
    
    # Calculate emergent intelligence metrics
    print("\n🧠 Calculating emergent intelligence metrics...")
    boids_ei = calculate_emergent_intelligence_metrics(boids_data)
    baseline_ei = calculate_emergent_intelligence_metrics(baseline_data)
    
    # TCI Statistics
    boids_tci_scores = [t for t in boids_data['all_tci_scores'] if t > 0]
    baseline_tci_scores = [t for t in baseline_data['all_tci_scores'] if t > 0]
    
    boids_tci_mean = statistics.mean(boids_tci_scores) if boids_tci_scores else 0
    baseline_tci_mean = statistics.mean(baseline_tci_scores) if baseline_tci_scores else 0
    
    print("\n📈 COMPREHENSIVE COMPARISON RESULTS")
    print("=" * 80)
    
    # 1. TCI Comparison
    print(f"\n🎯 1. TCI PERFORMANCE")
    print(f"{'Metric':<25} {'Boids':<12} {'Baseline':<12} {'Difference':<12} {'Winner':<10}")
    print("-" * 75)
    
    tci_diff = boids_tci_mean - baseline_tci_mean
    tci_winner = "🚀 BOIDS" if tci_diff > 0 else "⚖️ BASELINE"
    print(f"{'Mean TCI':<25} {boids_tci_mean:<12.3f} {baseline_tci_mean:<12.3f} {tci_diff:<12.3f} {tci_winner:<10}")
    
    boids_peak = max(boids_tci_scores) if boids_tci_scores else 0
    baseline_peak = max(baseline_tci_scores) if baseline_tci_scores else 0
    peak_diff = boids_peak - baseline_peak
    peak_winner = "🚀 BOIDS" if peak_diff > 0 else "⚖️ BASELINE"
    print(f"{'Peak TCI':<25} {boids_peak:<12.3f} {baseline_peak:<12.3f} {peak_diff:<12.3f} {peak_winner:<10}")
    
    # 2. Test Case Level Pass Rate (CORRECTED)
    print(f"\n✅ 2. TEST CASE LEVEL PASS RATE (CORRECTED)")
    print(f"{'Experiment':<15} {'Passed':<10} {'Total':<10} {'Pass Rate':<12} {'Winner':<10}")
    print("-" * 60)
    
    boids_pass_rate = boids_data['test_case_pass_rate'] * 100
    baseline_pass_rate = baseline_data['test_case_pass_rate'] * 100
    pass_rate_diff = boids_pass_rate - baseline_pass_rate
    pass_rate_winner = "🚀 BOIDS" if pass_rate_diff > 0 else "⚖️ BASELINE"
    
    print(f"{'Boids':<15} {boids_data['passed_test_cases']:<10} {boids_data['total_test_cases']:<10} {boids_pass_rate:<12.1f}%")
    print(f"{'Baseline':<15} {baseline_data['passed_test_cases']:<10} {baseline_data['total_test_cases']:<10} {baseline_pass_rate:<12.1f}%")
    print(f"{'Advantage':<15} {'':<10} {'':<10} {pass_rate_diff:<12.1f}pp {pass_rate_winner:<10}")
    
    # 3. Emergent Intelligence Metrics Comparison
    print(f"\n🧠 3. EMERGENT INTELLIGENCE METRICS")
    print(f"{'Metric':<25} {'Boids':<12} {'Baseline':<12} {'Difference':<12} {'Winner':<10}")
    print("-" * 75)
    
    ei_metrics = [
        ('Category Entropy', 'category_entropy'),
        ('Modularity Q', 'modularity_q'),
        ('Unique Pattern Ratio', 'unique_pattern_ratio'),
        ('Agent Complexity Var', 'agent_complexity_variance'),
        ('Specialization (NMI)', 'category_concentration'),
        ('Center Drift Rate', 'center_drift_rate')
    ]
    
    boids_ei_wins = 0
    baseline_ei_wins = 0
    
    for metric_name, metric_key in ei_metrics:
        boids_val = boids_ei.get(metric_key, 0)
        baseline_val = baseline_ei.get(metric_key, 0)
        diff = boids_val - baseline_val
        winner = "🚀 BOIDS" if diff > 0 else "⚖️ BASELINE"
        
        if diff > 0:
            boids_ei_wins += 1
        else:
            baseline_ei_wins += 1
        
        print(f"{metric_name:<25} {boids_val:<12.3f} {baseline_val:<12.3f} {diff:<12.3f} {winner:<10}")
    
    # 4. Emergent Intelligence Indicators
    print(f"\n🎯 4. EMERGENT INTELLIGENCE INDICATORS")
    print(f"{'Indicator':<30} {'Boids':<10} {'Baseline':<10} {'Winner':<10}")
    print("-" * 65)
    
    indicators = [
        ('Functional Emergence', 'category_entropy', 0.8),
        ('System Coherence', 'agent_complexity_variance', 0.6),
        ('Collective Innovation', 'unique_pattern_ratio', 0.7),
        ('Coordination Evidence', 'category_concentration', 0.6),
        ('Adaptive Learning', 'center_drift_rate', 0.5)
    ]
    
    boids_indicators = 0
    baseline_indicators = 0
    
    for indicator_name, metric_key, threshold in indicators:
        boids_val = boids_ei.get(metric_key, 0)
        baseline_val = baseline_ei.get(metric_key, 0)
        
        boids_indicator = "✅" if boids_val > threshold else "❌"
        baseline_indicator = "✅" if baseline_val > threshold else "❌"
        
        if boids_val > baseline_val:
            winner = "🚀 BOIDS"
            boids_indicators += 1
        else:
            winner = "⚖️ BASELINE"
            baseline_indicators += 1
        
        print(f"{indicator_name:<30} {boids_indicator:<10} {baseline_indicator:<10} {winner:<10}")
    
    # 5. Final Summary
    print(f"\n🏆 FINAL COMPREHENSIVE SUMMARY")
    print("=" * 50)
    
    total_categories = 4  # TCI, Pass Rate, EI Metrics, EI Indicators
    boids_category_wins = 0
    
    # Count category wins
    if tci_diff > 0:
        boids_category_wins += 1
        print(f"✅ TCI Performance: BOIDS WINS (+{tci_diff:.3f})")
    else:
        print(f"❌ TCI Performance: BASELINE WINS ({abs(tci_diff):.3f})")
    
    if pass_rate_diff > 0:
        boids_category_wins += 1
        print(f"✅ Test Case Pass Rate: BOIDS WINS (+{pass_rate_diff:.1f}pp)")
    else:
        print(f"❌ Test Case Pass Rate: BASELINE WINS ({abs(pass_rate_diff):.1f}pp)")
    
    if boids_ei_wins > baseline_ei_wins:
        boids_category_wins += 1
        print(f"✅ Emergent Intelligence Metrics: BOIDS WINS ({boids_ei_wins}/6)")
    else:
        print(f"❌ Emergent Intelligence Metrics: BASELINE WINS ({baseline_ei_wins}/6)")
    
    if boids_indicators > baseline_indicators:
        boids_category_wins += 1
        print(f"✅ Emergent Intelligence Indicators: BOIDS WINS ({boids_indicators}/5)")
    else:
        print(f"❌ Emergent Intelligence Indicators: BASELINE WINS ({baseline_indicators}/5)")
    
    print(f"\n🎉 OVERALL WINNER: ", end="")
    if boids_category_wins > total_categories / 2:
        print(f"🚀 BOIDS ({boids_category_wins}/{total_categories} categories)")
        print("🔥 Boids demonstrates superior emergent intelligence!")
    else:
        print(f"⚖️ BASELINE ({total_categories - boids_category_wins}/{total_categories} categories)")
        print("🔥 Baseline shows stronger traditional performance!")
    
    return {
        'boids_data': boids_data,
        'baseline_data': baseline_data,
        'boids_ei': boids_ei,
        'baseline_ei': baseline_ei,
        'summary': {
            'boids_category_wins': boids_category_wins,
            'total_categories': total_categories,
            'tci_advantage': tci_diff,
            'pass_rate_advantage': pass_rate_diff,
            'ei_metric_wins': boids_ei_wins,
            'ei_indicator_wins': boids_indicators
        }
    }

if __name__ == "__main__":
    results = analyze_experiments_comprehensive()
