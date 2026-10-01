#!/usr/bin/env python3
"""
Update metric names to be precise and concise
"""

# OLD NAME -> NEW NAME mapping
METRIC_RENAMES = {
    # Core metrics
    'adaptive_learning_score': 'center_drift_rate',
    'innovation_rate': 'unique_pattern_ratio', 
    'complexity_coherence': 'agent_complexity_variance',
    'emergent_specialization': 'category_concentration',
    'functional_diversity': 'category_entropy',
    'modularity_index': 'loc_consistency',
    
    # Display names for reports
    'Emergent Intelligence Score': 'Center Drift Rate',
    'Innovation Rate': 'Unique Pattern Ratio',
    'System Coherence': 'Agent Complexity Variance', 
    'Emergent Specialization': 'Category Concentration',
    'Functional Diversity': 'Category Entropy',
    'Modularity Index': 'LOC Consistency',
    'Adaptive Learning': 'Center Drift',
    'Collective Innovation': 'Pattern Uniqueness',
    'Coordination Evidence': 'Category Concentration',
    'System Coherence': 'Complexity Variance',
    'Functional Emergence': 'Category Entropy'
}

def update_analyzer_file():
    """Update the analyzer file with new metric names"""
    with open('experiment_result_analyzer.py', 'r') as f:
        content = f.read()
    
    # Update variable names and comments
    replacements = [
        ('adaptive_learning_score', 'center_drift_rate'),
        ('innovation_rate', 'unique_pattern_ratio'),
        ('complexity_coherence', 'agent_complexity_variance'),
        ('emergent_specialization', 'category_concentration'),
        ('functional_diversity', 'category_entropy'),
        ('modularity_index', 'loc_consistency'),
        
        # Update display strings
        ('Emergent Intelligence Score', 'Center Drift Rate'),
        ('Innovation Rate', 'Unique Pattern Ratio'),
        ('System Coherence', 'Agent Complexity Variance'),
        ('Emergent Specialization', 'Category Concentration'),
        ('Functional Diversity', 'Category Entropy'),
        ('Modularity Index', 'LOC Consistency'),
        ('Adaptive Learning', 'Center Drift'),
        ('Collective Innovation', 'Pattern Uniqueness'),
        ('Coordination Evidence', 'Category Concentration'),
        
        # Update comments to be precise
        ('measures how well the system adapts and evolves over time', 'measures semantic drift in collective center descriptions'),
        ('measures how frequently new functional patterns emerge', 'measures ratio of unique semantic fingerprints to total tools'),
        ('measures consistency in complexity patterns across agents', 'measures variance in agent average complexity scores'),
        ('degree of agent differentiation', 'concentration of agents in dominant categories'),
        ('Shannon entropy of categories', 'normalized Shannon entropy of tool categories'),
        ('based on LOC distribution', 'inverse coefficient of variation of LOC'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write updated content
    with open('experiment_result_analyzer.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated analyzer with precise metric names")

if __name__ == "__main__":
    update_analyzer_file()
