#!/usr/bin/env python3
"""
Experiment Runner for Agent Society v1
Enhanced with Comprehensive Testing Support!

Manages the complete experiment lifecycle:
- Setup with testing infrastructure
- Agent society simulation with testing
- Result collection and analysis
"""

import os
import shutil
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.azure_client import AzureOpenAIClient
from src.agent_v1 import Agent
from src.tools_v1 import ToolRegistryV1
from src.experiment_visualizer import ExperimentVisualizer
from src.complexity_analyzer import TCIAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Experiment Runner v1 - Enhanced with Testing Support
    
    Features:
    - Self-contained experiment directories
    - Comprehensive testing infrastructure
    - Agent society simulation with testing phases
    - Detailed result analysis and reporting
    """
    
    def __init__(self, 
                 experiment_name: str, 
                 num_agents: int, 
                 max_rounds: int, 
                 shared_meta_prompt: str,
                 agent_specializations: List[str] = None):
        
        self.experiment_name = experiment_name
        self.num_agents = num_agents
        self.max_rounds = max_rounds
        self.shared_meta_prompt = shared_meta_prompt
        self.agent_specializations = agent_specializations or []
        
        # Experiment paths - EVERYTHING goes inside the experiment directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.experiment_dir = f"experiments/{experiment_name}_{timestamp}"
        self.shared_tools_dir = os.path.join(self.experiment_dir, "shared_tools")
        self.personal_tools_dir = os.path.join(self.experiment_dir, "personal_tools")
        self.template_dir = "shared_tools_template"  # Source template stays at root
        
        # Results and logs
        self.results_file = os.path.join(self.experiment_dir, "results.json")
        self.summary_file = os.path.join(self.experiment_dir, "summary.txt")
        self.metadata_file = os.path.join(self.experiment_dir, "experiment_metadata.json")
        
        # Initialize components
        self.azure_client = None
        self.tool_registry = None
        self.agents = []
        self.round_results = []
        self.complexity_over_rounds = []  # Track average TCI per round
        self.visualizer = ExperimentVisualizer()
        self.tci_analyzer = TCIAnalyzer()
        
        logger.info(f"🧪 Experiment initialized: {self.experiment_name}")
        logger.info(f"📁 Experiment directory: {self.experiment_dir}")
    
    def _initialize_azure_client(self) -> bool:
        """Initialize Azure OpenAI client."""
        try:
            self.azure_client = AzureOpenAIClient()
            logger.info("✅ Azure OpenAI client initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Azure client initialization failed: {e}")
            return False
    
    def _initialize_shared_tools(self) -> bool:
        """Initialize shared tools from template."""
        try:
            # Create experiment directory
            os.makedirs(self.experiment_dir, exist_ok=True)
            
            # Initialize tool registry with experiment-specific paths
            self.tool_registry = ToolRegistryV1(
                shared_tools_dir=self.shared_tools_dir,
                personal_tools_base_dir=self.personal_tools_dir
            )
            
            logger.info("✅ Shared tools initialized from template")
            return True
            
        except Exception as e:
            logger.error(f"❌ Shared tools initialization failed: {e}")
            return False
    
    def _create_personal_tool_directories(self):
        """Create personal tool directories for each agent."""
        try:
            os.makedirs(self.personal_tools_dir, exist_ok=True)
            
            for i in range(1, self.num_agents + 1):
                agent_id = f"Agent_{i:02d}"
                agent_dir = os.path.join(self.personal_tools_dir, agent_id)
                
                # Create agent directory structure with testing support
                os.makedirs(agent_dir, exist_ok=True)
                os.makedirs(os.path.join(agent_dir, "_tests"), exist_ok=True)
                os.makedirs(os.path.join(agent_dir, "_testResults"), exist_ok=True)
                
                # Initialize empty index
                index_file = os.path.join(agent_dir, "index.json")
                if not os.path.exists(index_file):
                    with open(index_file, 'w') as f:
                        json.dump({"tools": {}}, f, indent=2)
                
                logger.info(f"📁 Created agent directory: {agent_id}")
            
            logger.info(f"✅ Personal tool directories created for {self.num_agents} agents")
            
        except Exception as e:
            logger.error(f"❌ Personal tool directories creation failed: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize all agents with their specializations."""
        try:
            for i in range(1, self.num_agents + 1):
                agent_id = f"Agent_{i:02d}"
                
                # Get specialization if available
                if i <= len(self.agent_specializations):
                    specialization = self.agent_specializations[i-1]
                else:
                    specialization = f"Focus on building practical tools for general use."
                
                # Create agent
                agent = Agent(
                    agent_id=agent_id,
                    azure_client=self.azure_client,
                    shared_tool_registry=self.tool_registry,
                    meta_prompt=self.shared_meta_prompt,
                    envs_available=["python", "file_system", "data_processing"],
                    specific_prompt=specialization,
                    personal_tool_base_dir=self.personal_tools_dir  # Use experiment-specific path
                )
                
                self.agents.append(agent)
                logger.info(f"🤖 Agent {agent_id} initialized with specialization: {specialization}")
            
            logger.info(f"✅ All {len(self.agents)} agents initialized")
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            raise
    
    def _run_single_round(self, round_num: int) -> Dict[str, Any]:
        """
        Run a single round of the agent society simulation.
        Enhanced with testing phases and beautiful visualization!
        """
        logger.info(f"\n🔄 Starting Round {round_num}")
        logger.info("=" * 50)
        
        # Show beautiful round header
        self.visualizer.show_round_header(round_num, self.max_rounds)
        
        round_results = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "agent_actions": [],
            "tools_created": 0,
            "tests_created": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tools_in_system": 0,
            "collaboration_events": 0  # Removed neighbor testing - pure agent cycle
        }
        
        # Phase 1: Observe and Reflect
        self.visualizer.show_phase_header("Phase 1: Agent Observation and Reflection", "🔍")
        
        for agent in self.agents:
            try:
                observation = agent.observe()
                reflection = agent.reflect(observation)
                
                # Show beautiful reflection visualization
                self.visualizer.show_agent_reflection(agent.agent_id, reflection, observation)
                
                logger.info(f"   {agent.agent_id}: Observed {len(observation['all_visible_tools'])} tools")
                logger.info(f"   {agent.agent_id}: Reflection generated")
                
            except Exception as e:
                logger.error(f"   ❌ {agent.agent_id} observation/reflection failed: {e}")
        
        # Phase 2: Build Tools
        self.visualizer.show_phase_header("Phase 2: Tool Building", "🔨")
        
        for agent in self.agents:
            try:
                # Get latest reflection
                if agent.reflection_history:
                    latest_reflection = agent.reflection_history[-1]["reflection"]
                    build_result = agent.build_tools(latest_reflection)
                    
                    # Show beautiful tool creation visualization
                    self.visualizer.show_tool_creation(agent.agent_id, build_result.get("tool_info", {}), build_result["success"])
                    
                    if build_result["success"]:
                        round_results["tools_created"] += 1
                        logger.info(f"   ✅ {agent.agent_id}: Built tool successfully")

                        # Phase 3a: Analyze Tool Complexity
                        logger.info(f"   🔬 Analyzing complexity for new tool...")
                        tool_name = build_result["tool_info"].get("tool_name")
                        if tool_name:
                            agent_tool_dir = agent.personal_tool_dir
                            # Analyze the entire directory to update compositional scores
                            tci_results = self.tci_analyzer.analyze_tools_directory(agent_tool_dir)
                            
                            # Update all tools for the agent with new scores
                            if tci_results:
                                for t_name, tci_data in tci_results.items():
                                    agent.update_tool_complexity(t_name, tci_data)
                        
                        # Phase 3b: Build Tests for the new tool
                        logger.info(f"   🧪 Building tests for {agent.agent_id}'s new tool...")
                        test_result = agent.build_tests(build_result["tool_info"])
                        
                        if test_result["success"]:
                            round_results["tests_created"] += 1
                            
                            # Check test results
                            test_results = test_result.get("test_results", {})
                            tool_name = build_result["tool_info"].get("tool_name", "unknown")
                            
                            # Show beautiful test execution visualization
                            self.visualizer.show_test_execution(agent.agent_id, tool_name, test_results)
                            
                            if test_results.get("all_passed"):
                                round_results["tests_passed"] += 1
                                logger.info(f"   ✅ {agent.agent_id}: Tests passed!")
                                # Promote the successful tool to the shared directory
                                self._promote_tool_to_shared(agent, tool_name)
                            else:
                                round_results["tests_failed"] += 1
                                logger.info(f"   ❌ {agent.agent_id}: Tests failed")
                        else:
                            logger.warning(f"   ⚠️  {agent.agent_id}: Test creation failed")
                    else:
                        logger.warning(f"   ⚠️  {agent.agent_id}: Tool building failed")
                        
                    # Record agent action
                    agent_action = {
                        "agent_id": agent.agent_id,
                        "tool_build_success": build_result["success"],
                        "test_build_success": test_result.get("success", False) if build_result["success"] else False,
                        "test_passed": test_result.get("test_results", {}).get("all_passed", False) if build_result["success"] else False,
                        "tools_built_so_far": len(agent.self_built_tools),
                        "tests_built_so_far": len(agent.self_built_tests)
                    }
                    round_results["agent_actions"].append(agent_action)
                    
            except Exception as e:
                logger.error(f"   ❌ {agent.agent_id} tool building failed: {e}")
        
        # Phase 4: Removed - Keep agent cycle pure (observe → reflect → build_tools → build_tests)
        
        # Phase 5: Calculate and Record System Complexity
        self._calculate_and_record_system_complexity(round_num)

        # Get total tools in system
        all_tools = self.tool_registry.get_all_tools()
        round_results["total_tools_in_system"] = len(all_tools)
        
        # Show beautiful round summary
        self.visualizer.show_round_summary(round_num, round_results)
        
        logger.info(f"\n📊 Round {round_num} Summary:")
        logger.info(f"   Tools created: {round_results['tools_created']}")
        logger.info(f"   Tests created: {round_results['tests_created']}")
        logger.info(f"   Tests passed: {round_results['tests_passed']}")
        logger.info(f"   Tests failed: {round_results['tests_failed']}")
        logger.info(f"   Total tools in system: {round_results['total_tools_in_system']}")
        logger.info(f"   Collaboration events: {round_results['collaboration_events']}")
        
        return round_results
    
    def _calculate_and_record_system_complexity(self, round_num: int):
        """Calculate the average TCI of all tools in the system at the end of a round."""
        all_tools_metadata = self.tool_registry.get_all_tools()
        total_tci = 0
        total_code_complexity = 0
        total_interface_complexity = 0
        total_compositional_complexity = 0
        tool_count = 0
        
        for tool_name, metadata in all_tools_metadata.items():
            complexity_data = metadata.get("complexity")
            if complexity_data and "tci_score" in complexity_data:
                total_tci += complexity_data.get("tci_score", 0)
                total_code_complexity += complexity_data.get("code_complexity", 0)
                total_interface_complexity += complexity_data.get("interface_complexity", 0)
                total_compositional_complexity += complexity_data.get("compositional_complexity", 0)
                tool_count += 1
        
        average_tci = total_tci / tool_count if tool_count > 0 else 0
        avg_code = total_code_complexity / tool_count if tool_count > 0 else 0
        avg_interface = total_interface_complexity / tool_count if tool_count > 0 else 0
        avg_compositional = total_compositional_complexity / tool_count if tool_count > 0 else 0

        self.complexity_over_rounds.append({
            "round": round_num,
            "average_tci": average_tci,
            "avg_code_complexity": avg_code,
            "avg_interface_complexity": avg_interface,
            "avg_compositional_complexity": avg_compositional,
            "tool_count": tool_count
        })
        logger.info(f"   📈 System Complexity: Avg TCI = {average_tci:.2f} across {tool_count} tools.")

    def _promote_tool_to_shared(self, agent, tool_name: str):
        """
        Copies a successful and tested tool from an agent's personal directory
        to the experiment's shared tools directory for all agents to use.
        """
        logger.info(f"   🤝 Promoting successful tool '{tool_name}' from {agent.agent_id} to shared library...")
        try:
            # 1. Define source and destination paths
            personal_index_file = os.path.join(agent.personal_tool_dir, "index.json")
            shared_index_file = os.path.join(self.shared_tools_dir, "index.json")

            src_tool_file = os.path.join(agent.personal_tool_dir, f"{tool_name}.py")
            dest_tool_file = os.path.join(self.shared_tools_dir, f"{tool_name}.py")

            src_test_file = os.path.join(agent.personal_tests_dir, f"{tool_name}_test.py")
            dest_test_dir = os.path.join(self.shared_tools_dir, "_tests")
            os.makedirs(dest_test_dir, exist_ok=True)
            dest_test_file = os.path.join(dest_test_dir, f"{tool_name}_test.py")

            src_results_file = os.path.join(agent.personal_test_results_dir, f"{tool_name}_results.json")
            dest_results_dir = os.path.join(self.shared_tools_dir, "_testResults")
            os.makedirs(dest_results_dir, exist_ok=True)
            dest_results_file = os.path.join(dest_results_dir, f"{tool_name}_results.json")

            # 2. Copy the tool, test, and results files
            shutil.copy2(src_tool_file, dest_tool_file)
            if os.path.exists(src_test_file):
                shutil.copy2(src_test_file, dest_test_file)
            if os.path.exists(src_results_file):
                shutil.copy2(src_results_file, dest_results_file)
            
            # 3. Load metadata from the agent's personal index
            personal_index_data = self._load_index_json(personal_index_file)
            tool_metadata = personal_index_data.get("tools", {}).get(tool_name)

            if tool_metadata:
                # 4. Add the tool's metadata to the shared index
                shared_index_data = self._load_index_json(shared_index_file)
                
                # Ensure paths in metadata are relative to the shared directory
                tool_metadata["file"] = f"{tool_name}.py"
                if os.path.exists(src_test_file):
                    tool_metadata["has_test"] = True
                    tool_metadata["test_file"] = f"_tests/{tool_name}_test.py"
                if os.path.exists(src_results_file):
                    tool_metadata["test_results_file"] = f"_testResults/{tool_name}_results.json"
                
                shared_index_data["tools"][tool_name] = tool_metadata
                self._save_index_json(shared_index_file, shared_index_data)
                logger.info(f"   ✅ Promoted '{tool_name}' to the shared tool index.")
            else:
                logger.warning(f"   ⚠️  Could not find metadata for '{tool_name}' in personal index during promotion.")

        except Exception as e:
            logger.error(f"   ❌ Failed to promote tool '{tool_name}': {e}")
            
    def _load_index_json(self, index_file: str) -> Dict[str, Any]:
        """DRY: Load index JSON with error handling."""
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading {index_file}: {e}")
                return {"tools": {}}
        return {"tools": {}}
    
    def _save_index_json(self, index_file: str, index_data: Dict[str, Any]) -> bool:
        """DRY: Save index JSON with error handling."""
        try:
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            return True
        except Exception as e:
            logger.warning(f"   ⚠️  Error saving {index_file}: {e}")
            return False

    def run_experiment(self):
        """Run the complete experiment with testing support."""
        logger.info(f"🚀 Starting Experiment: {self.experiment_name}")
        logger.info("=" * 60)
        
        # Show beautiful experiment header
        self.visualizer.show_experiment_header(self.experiment_name, self.num_agents, self.max_rounds)
        
        try:
            # 1. Initialize Azure client
            if not self._initialize_azure_client():
                return False
            
            # 2. Initialize shared tools
            if not self._initialize_shared_tools():
                return False
            
            # 3. Create personal tool directories
            self._create_personal_tool_directories()
            
            # 4. Initialize agents
            self._initialize_agents()
            
            # 5. Run simulation rounds
            logger.info(f"\n🔄 Running {self.max_rounds} rounds of agent society simulation")
            
            for round_num in range(1, self.max_rounds + 1):
                round_result = self._run_single_round(round_num)
                self.round_results.append(round_result)
                
                # Brief pause between rounds
                import time
                time.sleep(1)
            
            # 6. Save results and reflection histories
            self._save_experiment_results()
            self._save_all_reflection_histories()
            
            # Show beautiful experiment summary
            final_stats = self._collect_final_statistics()
            self.visualizer.show_experiment_summary(final_stats, self.experiment_dir)
            
            # Save visualization log
            self.visualizer.save_visualization_log(self.experiment_dir)
            
            logger.info(f"\n✅ Experiment completed successfully!")
            logger.info(f"📁 Results saved in: {self.experiment_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Experiment failed: {e}")
            return False
    
    def _save_experiment_results(self):
        """Save comprehensive experiment results with testing analysis."""
        
        # Collect final statistics
        final_stats = self._collect_final_statistics()
        
        # Save detailed results
        results_data = {
            "experiment_metadata": {
                "name": self.experiment_name,
                "num_agents": self.num_agents,
                "max_rounds": self.max_rounds,
                "shared_meta_prompt": self.shared_meta_prompt,
                "agent_specializations": self.agent_specializations,
                "experiment_dir": self.experiment_dir,
                "timestamp": datetime.now().isoformat()
            },
            "round_results": self.round_results,
            "complexity_over_rounds": self.complexity_over_rounds,  # Add breakdown data
            "final_statistics": final_stats,
            "agent_summaries": self._get_agent_summaries()
        }
        
        # Save JSON results
        with open(self.results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Save human-readable summary
        self._save_human_readable_summary(final_stats)
        
        # Save experiment metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(results_data["experiment_metadata"], f, indent=2)
        
        logger.info(f"💾 Results saved:")
        logger.info(f"   📄 Detailed results: {self.results_file}")
        logger.info(f"   📄 Summary: {self.summary_file}")
        logger.info(f"   📄 Metadata: {self.metadata_file}")
    
    def _collect_final_statistics(self) -> Dict[str, Any]:
        """Collect final experiment statistics with testing metrics."""
        
        # Get all tools with test status
        tools_with_tests = self.tool_registry.get_all_tools_with_test_status()
        
        stats = {
            "total_rounds": len(self.round_results),
            "total_tools_created": sum(r["tools_created"] for r in self.round_results),
            "total_tests_created": sum(r["tests_created"] for r in self.round_results),
            "total_tests_passed": sum(r["tests_passed"] for r in self.round_results),
            "total_tests_failed": sum(r["tests_failed"] for r in self.round_results),
            "total_collaboration_events": sum(r["collaboration_events"] for r in self.round_results),
            "final_tools_in_system": len(tools_with_tests),
            "testing_coverage": {
                "tools_with_tests": len([t for t in tools_with_tests.values() if t["has_test"]]),
                "tools_with_results": len([t for t in tools_with_tests.values() if t["has_results"]]),
                "tools_passed_tests": len([t for t in tools_with_tests.values() if t["test_passed"]]),
                "tools_failed_tests": len([t for t in tools_with_tests.values() if t["has_results"] and not t["test_passed"]])
            },
            "agent_productivity": {
                agent.agent_id: {
                    "tools_built": len(agent.self_built_tools),
                    "tests_built": len(agent.self_built_tests),
                    "reflections": len(agent.reflection_history),
                    "test_results": len(agent.test_results_history)
                }
                for agent in self.agents
            }
        }
        
        # Calculate rates
        if stats["total_tests_created"] > 0:
            stats["test_pass_rate"] = stats["total_tests_passed"] / stats["total_tests_created"]
        else:
            stats["test_pass_rate"] = 0.0
        
        if stats["final_tools_in_system"] > 0:
            stats["testing_coverage_rate"] = stats["testing_coverage"]["tools_with_tests"] / stats["final_tools_in_system"]
        else:
            stats["testing_coverage_rate"] = 0.0
        
        return stats
    
    def _get_agent_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed summaries for each agent."""
        summaries = {}
        
        for agent in self.agents:
            summaries[agent.agent_id] = {
                "specialization": agent.specific_prompt,
                "tools_built": agent.self_built_tools,
                "tests_built": agent.self_built_tests,
                "reflection_count": len(agent.reflection_history),
                "test_results_count": len(agent.test_results_history),
                "personal_tool_dir": agent.personal_tool_dir,
                "latest_reflection": agent.reflection_history[-1]["reflection"] if agent.reflection_history else None
            }
        
        return summaries
    
    def _save_human_readable_summary(self, final_stats: Dict[str, Any]):
        """Save a human-readable experiment summary."""
        
        with open(self.summary_file, 'w') as f:
            f.write(f"🧪 EXPERIMENT SUMMARY: {self.experiment_name}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 OVERVIEW:\n")
            f.write(f"   Experiment: {self.experiment_name}\n")
            f.write(f"   Agents: {self.num_agents}\n")
            f.write(f"   Rounds: {self.max_rounds}\n")
            f.write(f"   Directory: {self.experiment_dir}\n")
            f.write(f"   Timestamp: {datetime.now().isoformat()}\n\n")
            
            f.write(f"🔧 TOOL CREATION RESULTS:\n")
            f.write(f"   Total tools created: {final_stats['total_tools_created']}\n")
            f.write(f"   Final tools in system: {final_stats['final_tools_in_system']}\n")
            f.write(f"   Tools per round: {final_stats['total_tools_created'] / self.max_rounds:.1f}\n\n")
            
            f.write(f"🧪 TESTING RESULTS:\n")
            f.write(f"   Total tests created: {final_stats['total_tests_created']}\n")
            f.write(f"   Tests passed: {final_stats['total_tests_passed']}\n")
            f.write(f"   Tests failed: {final_stats['total_tests_failed']}\n")
            f.write(f"   Test pass rate: {final_stats['test_pass_rate']:.2%}\n")
            f.write(f"   Testing coverage: {final_stats['testing_coverage_rate']:.2%}\n\n")
            
            f.write(f"🤝 COLLABORATION:\n")
            f.write(f"   Collaboration events: {final_stats['total_collaboration_events']}\n")
            f.write(f"   Events per round: {final_stats['total_collaboration_events'] / self.max_rounds:.1f}\n\n")
            
            f.write(f"🤖 AGENT PRODUCTIVITY:\n")
            for agent_id, productivity in final_stats['agent_productivity'].items():
                f.write(f"   {agent_id}:\n")
                f.write(f"     Tools: {productivity['tools_built']}\n")
                f.write(f"     Tests: {productivity['tests_built']}\n")
                f.write(f"     Reflections: {productivity['reflections']}\n")
                f.write(f"     Test Results: {productivity['test_results']}\n")
            
            f.write(f"\n📁 EXPERIMENT FILES:\n")
            f.write(f"   Shared tools: {self.shared_tools_dir}/\n")
            f.write(f"   Personal tools: {self.personal_tools_dir}/\n")
            f.write(f"   Results: {self.results_file}\n")
            f.write(f"   Metadata: {self.metadata_file}\n")
    
    def _save_all_reflection_histories(self):
        """Save reflection histories for all agents."""
        logger.info("💭 Saving agent reflection histories...")
        
        for agent in self.agents:
            try:
                success = agent.save_reflection_history()
                if success:
                    logger.info(f"   ✅ {agent.agent_id}: {len(agent.reflection_history)} reflections saved")
                else:
                    logger.warning(f"   ⚠️  {agent.agent_id}: Failed to save reflections")
            except Exception as e:
                logger.error(f"   ❌ {agent.agent_id}: Error saving reflections: {e}")
        
        logger.info("💭 All reflection histories processing complete")


def main():
    """Run a sample experiment with testing support."""
    
    print("🧪 Starting Enhanced Agent Society Experiment with Testing!")
    print("=" * 70)
    
    # Define agent specializations
    specializations = [
        "Focus on building SORTING and ORDERING algorithms. Create tools for data organization.",
        "Focus on building MATHEMATICAL and CALCULATION tools. Create tools for numerical operations.",
        "Focus on building TEXT PROCESSING and STRING manipulation tools. Create tools for text analysis."
    ]# optional 
    
    # Create experiment runner
    runner = ExperimentRunner(
        experiment_name="enhanced_testing_demo",
        num_agents=1,
        max_rounds=3,
        shared_meta_prompt="You are in a collaborative tool-building ecosystem. Focus on creating high-quality, well-tested tools that can be used by other agents. Focus on building data science tools.",
        agent_specializations=specializations
    )
    
    # Run the experiment
    success = runner.run_experiment()
    
    if success:
        print(f"\n✅ Experiment completed successfully!")
        print(f"📁 Check results in: {runner.experiment_dir}")
        
        # Show directory structure
        print(f"\n📂 Experiment Directory Structure:")
        for root, dirs, files in os.walk(runner.experiment_dir):
            level = root.replace(runner.experiment_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    else:
        print(f"\n❌ Experiment failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 