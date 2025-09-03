#!/usr/bin/env python3
"""
Tool Complexity Index (TCI) Analyzer
=====================================

Implements the 3-dimensional Tool Complexity Index framework:
1. Code Complexity (C_code): static structural complexity
2. Interface Complexity (C_iface): API richness and parameter complexity  
3. Compositional Complexity (C_comp): ecosystem role and dependencies

Usage:
    python complexity_analyzer.py --analyze shared_tools_template
    python complexity_analyzer.py --experiment experiments/enhanced_testing_demo_20250902_082953
"""

import os
import ast
import json
import argparse
import importlib.util
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import statistics
import math


class CodeComplexityAnalyzer:
    """Analyzes static code complexity metrics."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset metrics for new analysis."""
        self.cyclomatic_complexity = 0
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.lines_of_code = 0
        self.num_functions = 0
        self.num_branches = 0
        self.num_loops = 0
        
    def analyze_file(self, file_path: str) -> Dict[str, float]:
        """Analyze code complexity of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self.reset()
            self.lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            
            self._analyze_node(tree, depth=0)
            
            # Calculate composite code complexity score
            base_score = (
                self.cyclomatic_complexity * 0.3 +
                self.cognitive_complexity * 0.2 +
                self.nesting_depth * 0.2 +
                (self.lines_of_code / 10) * 0.15 +  # Normalize LOC
                self.num_branches * 0.1 +
                self.num_loops * 0.05
            )
            
            return {
                'code_complexity_score': base_score,
                'cyclomatic_complexity': self.cyclomatic_complexity,
                'cognitive_complexity': self.cognitive_complexity,
                'nesting_depth': self.nesting_depth,
                'lines_of_code': self.lines_of_code,
                'num_functions': self.num_functions,
                'num_branches': self.num_branches,
                'num_loops': self.num_loops
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {'code_complexity_score': 0.0}
    
    def _analyze_node(self, node: ast.AST, depth: int = 0):
        """Recursively analyze AST nodes for complexity metrics."""
        self.nesting_depth = max(self.nesting_depth, depth)
        
        if isinstance(node, ast.FunctionDef):
            self.num_functions += 1
            self.cyclomatic_complexity += 1  # Base complexity
            
        elif isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            self.cyclomatic_complexity += 1
            self.cognitive_complexity += (depth + 1)  # Nested complexity
            
            if isinstance(node, (ast.While, ast.For, ast.AsyncFor)):
                self.num_loops += 1
            else:
                self.num_branches += 1
                
        elif isinstance(node, (ast.ExceptHandler, ast.With, ast.AsyncWith)):
            self.cyclomatic_complexity += 1
            
        elif isinstance(node, ast.BoolOp):
            # Each additional condition in boolean operations
            self.cyclomatic_complexity += len(node.values) - 1
            
        # Recurse into child nodes
        for child in ast.iter_child_nodes(node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                self._analyze_node(child, depth + 1)
            else:
                self._analyze_node(child, depth)


class InterfaceComplexityAnalyzer:
    """Analyzes tool interface complexity."""
    
    def analyze_tool(self, tool_path: str) -> Dict[str, float]:
        """Analyze interface complexity of a tool."""
        try:
            # Load and execute tool to analyze its interface
            spec = importlib.util.spec_from_file_location("tool", tool_path)
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)
            
            if not hasattr(tool_module, 'execute'):
                return {'interface_complexity_score': 0.0}
            
            # Analyze the execute function signature and behavior
            execute_func = tool_module.execute
            
            # Test with different parameter structures to understand interface
            interface_metrics = self._probe_interface(execute_func)
            
            # Calculate composite interface complexity
            score = (
                interface_metrics['param_complexity'] * 0.4 +
                interface_metrics['return_complexity'] * 0.3 +
                interface_metrics['error_handling'] * 0.2 +
                interface_metrics['context_usage'] * 0.1
            )
            
            return {
                'interface_complexity_score': score,
                **interface_metrics
            }
            
        except Exception as e:
            print(f"Error analyzing interface for {tool_path}: {e}")
            return {'interface_complexity_score': 0.0}
    
    def _probe_interface(self, execute_func) -> Dict[str, float]:
        """Probe the tool interface to understand its complexity."""
        metrics = {
            'param_complexity': 0.0,
            'return_complexity': 0.0,
            'error_handling': 0.0,
            'context_usage': 0.0
        }
        
        # Test basic parameter handling
        test_cases = [
            {},  # Empty params
            {'data': [1, 2, 3]},  # Simple data
            {'data': [1, 2, 3], 'key': 'test'},  # Multiple params
            {'data': [{'a': 1}, {'b': 2}], 'nested': {'deep': {'value': 1}}},  # Complex nested
        ]
        
        results = []
        for params in test_cases:
            try:
                result = execute_func(params)
                results.append(result)
            except Exception:
                results.append(None)
        
        # Analyze parameter complexity
        metrics['param_complexity'] = self._calculate_param_complexity(test_cases, results)
        
        # Analyze return complexity
        metrics['return_complexity'] = self._calculate_return_complexity(results)
        
        # Check error handling
        try:
            error_result = execute_func({'invalid': 'params'})
            metrics['error_handling'] = 1.0 if isinstance(error_result, dict) and 'error' in error_result else 0.5
        except Exception:
            metrics['error_handling'] = 0.0
        
        # Check context usage
        try:
            context_result = execute_func({'data': [1, 2, 3]}, context={'test': True})
            metrics['context_usage'] = 1.0 if context_result != execute_func({'data': [1, 2, 3]}) else 0.0
        except Exception:
            metrics['context_usage'] = 0.0
            
        return metrics
    
    def _calculate_param_complexity(self, test_cases: List[Dict], results: List) -> float:
        """Calculate parameter complexity based on successful handling of different input types."""
        successful_cases = sum(1 for r in results if r is not None)
        complexity_levels = [len(str(case)) for case in test_cases]  # Rough measure of param complexity
        avg_complexity = statistics.mean(complexity_levels) if complexity_levels else 0
        return min(successful_cases * (avg_complexity / 100), 5.0)  # Cap at 5.0
    
    def _calculate_return_complexity(self, results: List) -> float:
        """Calculate return value complexity."""
        if not results:
            return 0.0
        
        complexity_scores = []
        for result in results:
            if result is None:
                complexity_scores.append(0.0)
            elif isinstance(result, dict):
                # Count keys, nesting depth, etc.
                score = len(result) * 0.2 + self._dict_depth(result) * 0.5
                complexity_scores.append(min(score, 3.0))
            else:
                complexity_scores.append(0.5)  # Simple return type
        
        return statistics.mean(complexity_scores) if complexity_scores else 0.0
    
    def _dict_depth(self, d: Dict, depth: int = 0) -> int:
        """Calculate nesting depth of dictionary."""
        if not isinstance(d, dict):
            return depth
        return max([self._dict_depth(v, depth + 1) for v in d.values()] + [depth])


class CompositionalComplexityAnalyzer:
    """Analyzes compositional complexity within an ecosystem."""
    
    def __init__(self):
        self.dependency_graph = {}
        self.usage_counts = {}
        self.tool_relationships = {}
    
    def analyze_ecosystem(self, tools_dir: str) -> Dict[str, Dict[str, float]]:
        """Analyze compositional complexity for all tools in an ecosystem."""
        tool_files = list(Path(tools_dir).glob("*.py"))
        tool_names = [f.stem for f in tool_files if f.stem != '__init__']
        
        # Build dependency graph by analyzing tool code for context.call_tool usage
        for tool_file in tool_files:
            if tool_file.stem == '__init__':
                continue
            self._analyze_tool_dependencies(tool_file, tool_names)
        
        # Calculate compositional complexity for each tool
        complexity_scores = {}
        for tool_name in tool_names:
            complexity_scores[tool_name] = self._calculate_compositional_complexity(tool_name)
        
        return complexity_scores
    
    def _analyze_tool_dependencies(self, tool_file: Path, all_tools: List[str]):
        """Analyze dependencies of a single tool."""
        try:
            with open(tool_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tool_name = tool_file.stem
            dependencies = []
            
            # Look for context.call_tool usage
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Attribute) and 
                        isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'context' and 
                        node.func.attr == 'call_tool'):
                        
                        # Extract tool name from first argument
                        if node.args and isinstance(node.args[0], ast.Str):
                            dep_tool = node.args[0].s
                            if dep_tool in all_tools:
                                dependencies.append(dep_tool)
                        elif node.args and isinstance(node.args[0], ast.Constant):
                            dep_tool = node.args[0].value
                            if isinstance(dep_tool, str) and dep_tool in all_tools:
                                dependencies.append(dep_tool)
            
            self.dependency_graph[tool_name] = dependencies
            
        except Exception as e:
            print(f"Error analyzing dependencies for {tool_file}: {e}")
            self.dependency_graph[tool_file.stem] = []
    
    def _calculate_compositional_complexity(self, tool_name: str) -> Dict[str, float]:
        """Calculate compositional complexity metrics for a tool."""
        dependencies = self.dependency_graph.get(tool_name, [])
        
        # Calculate dependency depth (how deep the dependency chain goes)
        dependency_depth = self._calculate_dependency_depth(tool_name, visited=set())
        
        # Calculate fan-out (how many tools this tool depends on)
        fan_out = len(dependencies)
        
        # Calculate fan-in (how many tools depend on this tool)
        fan_in = sum(1 for deps in self.dependency_graph.values() if tool_name in deps)
        
        # Calculate reuse frequency (how often this tool is used)
        reuse_frequency = fan_in
        
        # Composite score
        composition_score = (
            dependency_depth * 0.4 +
            fan_out * 0.3 +
            fan_in * 0.2 +
            min(reuse_frequency, 5) * 0.1  # Cap reuse at 5
        )
        
        return {
            'compositional_complexity_score': composition_score,
            'dependency_depth': dependency_depth,
            'fan_out': fan_out,
            'fan_in': fan_in,
            'reuse_frequency': reuse_frequency
        }
    
    def _calculate_dependency_depth(self, tool_name: str, visited: set) -> int:
        """Calculate maximum dependency depth for a tool."""
        if tool_name in visited:
            return 0  # Avoid cycles
        
        visited.add(tool_name)
        dependencies = self.dependency_graph.get(tool_name, [])
        
        if not dependencies:
            return 0
        
        max_depth = max([self._calculate_dependency_depth(dep, visited.copy()) for dep in dependencies])
        return max_depth + 1


class TCIAnalyzer:
    """Main Tool Complexity Index analyzer."""
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0, gamma: float = 1.0):
        """Initialize with complexity dimension weights."""
        self.alpha = alpha  # Code complexity weight
        self.beta = beta    # Interface complexity weight
        self.gamma = gamma  # Compositional complexity weight
        
        self.code_analyzer = CodeComplexityAnalyzer()
        self.interface_analyzer = InterfaceComplexityAnalyzer()
        self.composition_analyzer = CompositionalComplexityAnalyzer()
    
    def analyze_tools_directory(self, tools_dir: str) -> Dict[str, Dict[str, Any]]:
        """Analyze all tools in a directory and calculate TCI scores."""
        tools_path = Path(tools_dir)
        if not tools_path.exists():
            raise FileNotFoundError(f"Tools directory not found: {tools_dir}")
        
        tool_files = list(tools_path.glob("*.py"))
        tool_files = [f for f in tool_files if f.stem != '__init__']
        
        if not tool_files:
            print(f"No Python files found in {tools_dir}")
            return {}
        
        results = {}
        
        print(f"🔍 Analyzing {len(tool_files)} tools in {tools_dir}")
        
        # Analyze compositional complexity for the ecosystem
        composition_scores = self.composition_analyzer.analyze_ecosystem(tools_dir)
        
        # Analyze each tool
        for tool_file in tool_files:
            tool_name = tool_file.stem
            print(f"   📊 Analyzing {tool_name}...")
            
            # Code complexity
            code_metrics = self.code_analyzer.analyze_file(str(tool_file))
            
            # Interface complexity
            interface_metrics = self.interface_analyzer.analyze_tool(str(tool_file))
            
            # Compositional complexity
            comp_metrics = composition_scores.get(tool_name, {'compositional_complexity_score': 0.0})
            
            # Calculate TCI
            c_code = code_metrics.get('code_complexity_score', 0.0)
            c_iface = interface_metrics.get('interface_complexity_score', 0.0)
            c_comp = comp_metrics.get('compositional_complexity_score', 0.0)
            
            raw_tci = self.alpha * c_code + self.beta * c_iface + self.gamma * c_comp
            
            # Store comprehensive results
            results[tool_name] = {
                'tci_score': raw_tci,
                'code_complexity': c_code,
                'interface_complexity': c_iface,
                'compositional_complexity': c_comp,
                'detailed_metrics': {
                    'code': code_metrics,
                    'interface': interface_metrics,
                    'composition': comp_metrics
                }
            }
        
        # Normalize TCI scores within this tool class
        if results:
            tci_scores = [r['tci_score'] for r in results.values()]
            if max(tci_scores) > 0:
                for tool_name in results:
                    results[tool_name]['tci_normalized'] = results[tool_name]['tci_score'] / max(tci_scores)
            else:
                for tool_name in results:
                    results[tool_name]['tci_normalized'] = 0.0
        
        return results
    
    def calculate_tci_lite(self, tool_file_path: str) -> Dict[str, Any]:
        """
        Calculates the TCI-lite score based on the simple P+D+G+L formula.
        P: Parameters (0-5)
        D: Dependencies (0-2)
        G: Guards (0-2)
        L: Lines of Code (0-3)
        Total score: 0-12 (will be scaled to 0-10)
        """
        try:
            with open(tool_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            print(f"Error parsing {tool_file_path} for TCI-lite: {e}")
            return {"tci_lite_score": 0, "P": 0, "D": 0, "G": 0, "L": 0}

        # L (LoC): Lines of Code
        loc = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
        if loc <= 60: L = 1
        elif loc <= 200: L = 2
        else: L = 3

        # D (Deps): Dependencies
        deps_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)])
        D = min(deps_count, 2)

        # P (Parameters) and G (Guards)
        params_count = 0
        guards_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Heuristic: find the main 'execute' or public function
                if not node.name.startswith('_'):
                    params_count = len(node.args.args)
            if isinstance(node, ast.If):
                # Heuristic for guards: check for 'error', 'exception', 'invalid' in condition
                condition_str = ast.dump(node.test).lower()
                if any(kw in condition_str for kw in ['error', 'exception', 'invalid', 'none']):
                    guards_count += 1
            if isinstance(node, ast.Try):
                guards_count += len(node.handlers)
        
        P = min(params_count, 5)
        G = min(guards_count, 2)

        # Calculate raw TCI-lite score (0-12)
        raw_score = P + D + G + L
        # Scale to 0-10 for final score
        scaled_score = round((raw_score / 12) * 10, 2)

        return {
            "tci_lite_score": scaled_score,
            "P": P,
            "D": D,
            "G": G,
            "L": L
        }

    def generate_report(self, results: Dict[str, Dict[str, Any]], output_file: Optional[str] = None) -> str:
        """Generate a comprehensive TCI analysis report."""
        if not results:
            return "No tools analyzed."
        
        report_lines = [
            "=" * 80,
            "TOOL COMPLEXITY INDEX (TCI) ANALYSIS REPORT", 
            "=" * 80,
            f"📊 Analyzed {len(results)} tools",
            f"⚖️  Weights: α={self.alpha} (code), β={self.beta} (interface), γ={self.gamma} (composition)",
            "",
            "📈 COMPLEXITY RANKINGS:",
            "-" * 40
        ]
        
        # Sort by TCI score
        sorted_tools = sorted(results.items(), key=lambda x: x[1]['tci_score'], reverse=True)
        
        for rank, (tool_name, metrics) in enumerate(sorted_tools, 1):
            report_lines.append(
                f"{rank:2d}. {tool_name:<20} TCI: {metrics['tci_score']:6.2f} "
                f"(Code: {metrics['code_complexity']:4.1f}, "
                f"Interface: {metrics['interface_complexity']:4.1f}, "
                f"Composition: {metrics['compositional_complexity']:4.1f})"
            )
        
        report_lines.extend([
            "",
            "📊 COMPLEXITY DISTRIBUTION:",
            "-" * 40
        ])
        
        tci_scores = [r['tci_score'] for r in results.values()]
        code_scores = [r['code_complexity'] for r in results.values()]
        iface_scores = [r['interface_complexity'] for r in results.values()]
        comp_scores = [r['compositional_complexity'] for r in results.values()]
        
        report_lines.extend([
            f"TCI Scores     - Mean: {statistics.mean(tci_scores):5.2f}, Std: {statistics.stdev(tci_scores) if len(tci_scores) > 1 else 0:5.2f}, Range: [{min(tci_scores):4.1f}, {max(tci_scores):4.1f}]",
            f"Code Scores    - Mean: {statistics.mean(code_scores):5.2f}, Std: {statistics.stdev(code_scores) if len(code_scores) > 1 else 0:5.2f}, Range: [{min(code_scores):4.1f}, {max(code_scores):4.1f}]",
            f"Interface      - Mean: {statistics.mean(iface_scores):5.2f}, Std: {statistics.stdev(iface_scores) if len(iface_scores) > 1 else 0:5.2f}, Range: [{min(iface_scores):4.1f}, {max(iface_scores):4.1f}]",
            f"Compositional  - Mean: {statistics.mean(comp_scores):5.2f}, Std: {statistics.stdev(comp_scores) if len(comp_scores) > 1 else 0:5.2f}, Range: [{min(comp_scores):4.1f}, {max(comp_scores):4.1f}]",
            "",
            "🔍 DETAILED ANALYSIS:",
            "-" * 40
        ])
        
        # Detailed breakdown for top 3 most complex tools
        for i, (tool_name, metrics) in enumerate(sorted_tools[:3]):
            report_lines.extend([
                f"",
                f"🏆 #{i+1} MOST COMPLEX: {tool_name}",
                f"   TCI Score: {metrics['tci_score']:.2f} (normalized: {metrics['tci_normalized']:.2f})",
                f"   Code Complexity: {metrics['code_complexity']:.2f}",
                f"     - Cyclomatic: {metrics['detailed_metrics']['code'].get('cyclomatic_complexity', 0)}",
                f"     - Lines of Code: {metrics['detailed_metrics']['code'].get('lines_of_code', 0)}",
                f"     - Nesting Depth: {metrics['detailed_metrics']['code'].get('nesting_depth', 0)}",
                f"   Interface Complexity: {metrics['interface_complexity']:.2f}",
                f"   Compositional Complexity: {metrics['compositional_complexity']:.2f}",
                f"     - Fan-in: {metrics['detailed_metrics']['composition'].get('fan_in', 0)}",
                f"     - Fan-out: {metrics['detailed_metrics']['composition'].get('fan_out', 0)}",
                f"     - Dependency Depth: {metrics['detailed_metrics']['composition'].get('dependency_depth', 0)}"
            ])
        
        report_lines.append("=" * 80)
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Tool Complexity Index (TCI) Analyzer")
    parser.add_argument("--analyze", required=True, help="Directory containing tools to analyze")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--alpha", type=float, default=1.0, help="Code complexity weight")
    parser.add_argument("--beta", type=float, default=1.0, help="Interface complexity weight") 
    parser.add_argument("--gamma", type=float, default=1.0, help="Compositional complexity weight")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TCIAnalyzer(alpha=args.alpha, beta=args.beta, gamma=args.gamma)
    
    try:
        # Analyze tools
        results = analyzer.analyze_tools_directory(args.analyze)
        
        if results:
            # Generate and display report
            report = analyzer.generate_report(results, args.output)
            print(report)
            
            # Save detailed JSON results
            json_output = args.output.replace('.txt', '.json') if args.output else 'tci_analysis.json'
            with open(json_output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"📊 Detailed results saved to: {json_output}")
        else:
            print("❌ No tools found to analyze.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 