#!/usr/bin/env python3
"""
Tool Ecosystem Analyzer - Visualize emergent collaboration patterns
"""

import json
import sys
from collections import defaultdict

def load_results(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_tool_ecosystem(data):
    print("🧬 TOOL ECOSYSTEM ANALYSIS")
    print("="*60)
    
    # Agent specializations
    print("\n🎯 AGENT SPECIALIZATIONS:")
    for agent_state in data['agent_states']:
        agent_id = agent_state['agent_id']
        spec = agent_state['specialization']
        tools = agent_state['tools']
        
        print(f"\n{agent_id}:")
        print(f"   🏆 Primary Type: {spec['primary_type']}")
        print(f"   �� Diversity: {spec['diversity_index']:.2f} (0=specialized, 1=diverse)")
        print(f"   🔧 Total Tools: {len(tools)}")
        print(f"   📈 Distribution: {spec['type_distribution']}")
    
    # Dependency network
    print("\n🔗 TOOL DEPENDENCY NETWORK:")
    all_tools = []
    for agent_state in data['agent_states']:
        all_tools.extend(agent_state['tools'])
    
    # Build dependency graph
    dependency_graph = defaultdict(list)
    for tool in all_tools:
        if tool['dependencies']:
            for dep in tool['dependencies']:
                dependency_graph[dep].append(tool['name'])
    
    # Show dependency chains
    for base_tool, dependent_tools in dependency_graph.items():
        print(f"\n   📦 {base_tool}")
        for dep_tool in dependent_tools:
            print(f"      └→ {dep_tool}")
    
    # Collaboration statistics
    tools_with_deps = [t for t in all_tools if t['dependencies']]
    print(f"\n📊 COLLABORATION STATISTICS:")
    print(f"   🤝 Collaborative Tools: {len(tools_with_deps)}/{len(all_tools)} ({len(tools_with_deps)/len(all_tools)*100:.1f}%)")
    
    # Cross-agent collaboration
    cross_agent_deps = 0
    for tool in tools_with_deps:
        tool_creator = tool['creator']
        for dep in tool['dependencies']:
            dep_creator = dep.split('_')[0] + '_' + dep.split('_')[1]  # Extract creator from tool name
            if dep_creator != tool_creator:
                cross_agent_deps += 1
    
    print(f"   🌐 Cross-Agent Dependencies: {cross_agent_deps}")
    print(f"   🔄 Self-Dependencies: {len(tools_with_deps) - cross_agent_deps}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <results_file.json>")
        return
    
    filename = sys.argv[1]
    data = load_results(filename)
    analyze_tool_ecosystem(data)

if __name__ == "__main__":
    main()
