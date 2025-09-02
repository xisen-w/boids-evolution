#!/usr/bin/env python3
"""
Run Experiment - Agentic Society Simulation Runner

Manages the complete lifecycle of agentic society experiments:
1. Initialize experiment environment
2. Set up shared tools from template
3. Create personal tool directories for each agent
4. Run agent society simulation
5. Log and analyze results
"""

import os
import sys
import json
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.append('src')

from src.agent_v1 import Agent
from src.tools_v1 import ToolRegistryV1, initialize_tool_system
from src.azure_client import AzureOpenAIClient


class ExperimentRunner:
    """
    Manages agentic society experiments with complete lifecycle management.
    """
    
    def __init__(self, 
                 experiment_name: str,
                 num_agents: int = 3,
                 max_rounds: int = 10,
                 shared_meta_prompt: str = "",
                 agent_specializations: Optional[List[str]] = None):
        
        self.experiment_name = experiment_name
        self.num_agents = num_agents
        self.max_rounds = max_rounds
        self.shared_meta_prompt = shared_meta_prompt
        self.agent_specializations = agent_specializations or []
        
        # Experiment paths - EVERYTHING goes inside the experiment directory
        self.experiment_dir = f"experiments/{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.shared_tools_dir = os.path.join(self.experiment_dir, "shared_tools")
        self.personal_tools_dir = os.path.join(self.experiment_dir, "personal_tools")
        self.template_dir = "shared_tools_template_legacy"  # Source template stays at root
        
        # Components
        self.azure_client = None
        self.tool_registry = None
        self.agents = []
        self.experiment_log = []
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up experiment logging."""
        os.makedirs(self.experiment_dir, exist_ok=True)
        
        log_file = os.path.join(self.experiment_dir, "experiment.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def initialize_experiment(self) -> bool:
        """
        Initialize the complete experiment environment.
        
        Returns:
            bool: Success status
        """
        self.logger.info(f"🧬 Initializing Experiment: {self.experiment_name}")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Initialize Azure client
            self.logger.info("Step 1: Initialize Azure OpenAI client")
            self.azure_client = AzureOpenAIClient()
            self.logger.info("✅ Azure client initialized")
            
            # Step 2: Initialize shared tools from template
            self.logger.info("Step 2: Initialize shared tools")
            success = self._initialize_shared_tools()
            if not success:
                self.logger.error("❌ Failed to initialize shared tools")
                return False
            
            # Step 3: Initialize tool registry
            self.logger.info("Step 3: Initialize tool registry")
            self.tool_registry = ToolRegistryV1(self.shared_tools_dir)
            self.logger.info("✅ Tool registry initialized")
            
            # Step 4: Create personal tool directories
            self.logger.info("Step 4: Create personal tool directories")
            self._create_personal_tool_directories()
            
            # Step 5: Create agents
            self.logger.info("Step 5: Create agents")
            self._create_agents()
            
            self.logger.info("🎯 Experiment initialization completed!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Experiment initialization failed: {e}")
            return False
    
    def _initialize_shared_tools(self) -> bool:
        """Initialize shared tools by copying from template into experiment directory."""
        
        try:
            # Create experiment directory first
            os.makedirs(self.experiment_dir, exist_ok=True)
            
            # Create shared tools directory inside experiment
            os.makedirs(self.shared_tools_dir, exist_ok=True)
            
            # Copy from template
            if os.path.exists(self.template_dir):
                self.logger.info(f"   📂 Copying tools from {self.template_dir} to {self.shared_tools_dir}")
                
                copied_files = 0
                for item in os.listdir(self.template_dir):
                    if item == "__pycache__":
                        continue
                        
                    source_path = os.path.join(self.template_dir, item)
                    dest_path = os.path.join(self.shared_tools_dir, item)
                    
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, dest_path)
                        copied_files += 1
                        self.logger.info(f"      ✅ Copied {item}")
                
                self.logger.info(f"   🎯 Shared tools initialized with {copied_files} files")
                return True
                
            else:
                self.logger.warning(f"   ⚠️  Template {self.template_dir} not found, creating empty shared tools")
                # Create empty index
                empty_index = {"tools": {}}
                with open(os.path.join(self.shared_tools_dir, "index.json"), 'w') as f:
                    json.dump(empty_index, f, indent=2)
                return True
                
        except Exception as e:
            self.logger.error(f"   ❌ Error initializing shared tools: {e}")
            return False
    
    def _create_personal_tool_directories(self):
        """Create personal tool directories for each agent inside experiment directory."""
        
        # Create personal tools base directory inside experiment
        os.makedirs(self.personal_tools_dir, exist_ok=True)
        
        # Create directory for each agent
        for i in range(self.num_agents):
            agent_id = f"Agent_{i+1:02d}"
            agent_dir = os.path.join(self.personal_tools_dir, agent_id)
            
            os.makedirs(agent_dir, exist_ok=True)
            
            # Create empty index.json for each agent
            empty_index = {
                "tools": {},
                "metadata": {
                    "agent_id": agent_id,
                    "total_tools": 0,
                    "created_at": datetime.now().isoformat(),
                    "experiment": self.experiment_name,
                    "experiment_dir": self.experiment_dir
                }
            }
            
            index_file = os.path.join(agent_dir, "index.json")
            with open(index_file, 'w') as f:
                json.dump(empty_index, f, indent=2)
            
            self.logger.info(f"   📁 Created directory: {agent_dir}")
        
        self.logger.info(f"   🎯 Created {self.num_agents} personal tool directories in {self.personal_tools_dir}")
    
    def _create_agents(self):
        """Create agent instances with specializations."""
        
        self.agents = []
        
        for i in range(self.num_agents):
            agent_id = f"Agent_{i+1:02d}"
            
            # Get specialization for this agent
            if i < len(self.agent_specializations):
                specialization = self.agent_specializations[i]
                specific_prompt = f"Your specialty is {specialization}. Focus on building tools related to {specialization}."
            else:
                specialization = "general"
                specific_prompt = None
            
            # Create agent
            agent = Agent(
                agent_id=agent_id,
                azure_client=self.azure_client,
                shared_tool_registry=self.tool_registry,
                meta_prompt=self.shared_meta_prompt,
                envs_available=["python", "file_system", "data_processing"],
                specific_prompt=specific_prompt,
                personal_tool_base_dir=self.personal_tools_dir  # Use experiment-specific directory
            )
            
            self.agents.append(agent)
            self.logger.info(f"   🤖 Created {agent_id} (specialization: {specialization})")
        
        self.logger.info(f"   🎯 Created {len(self.agents)} agents")
    
    def run_experiment(self) -> Dict[str, Any]:
        """
        Run the complete agentic society experiment.
        
        Returns:
            Dict with experiment results
        """
        self.logger.info(f"🚀 Starting Experiment Simulation")
        self.logger.info("=" * 60)
        
        experiment_results = {
            "experiment_name": self.experiment_name,
            "num_agents": self.num_agents,
            "max_rounds": self.max_rounds,
            "start_time": datetime.now().isoformat(),
            "rounds": []
        }
        
        for round_num in range(1, self.max_rounds + 1):
            self.logger.info(f"\n🔄 Round {round_num}/{self.max_rounds}")
            self.logger.info("-" * 40)
            
            round_results = self._run_round(round_num)
            experiment_results["rounds"].append(round_results)
            
            # Log round summary
            self._log_round_summary(round_num, round_results)
        
        experiment_results["end_time"] = datetime.now().isoformat()
        experiment_results["final_analysis"] = self._analyze_experiment_results()
        
        # Save results
        self._save_experiment_results(experiment_results)
        
        self.logger.info(f"\n🎯 Experiment completed!")
        return experiment_results
    
    def _run_round(self, round_num: int) -> Dict[str, Any]:
        """Run a single round where each agent acts."""
        
        round_results = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "agent_actions": []
        }
        
        for agent in self.agents:
            self.logger.info(f"   🤖 {agent.agent_id} acting...")
            
            try:
                # Agent observes, reflects, and acts
                observation = agent.observe()
                reflection = agent.reflect(observation)
                build_result = agent.build_tools(reflection)
                
                action_result = {
                    "agent_id": agent.agent_id,
                    "observation_summary": {
                        "visible_tools_count": len(observation["all_visible_tools"]),
                        "neighbor_tools": observation["neighbor_tools"],
                        "my_tools_count": len(observation["my_tools"])
                    },
                    "reflection": reflection[:200] + "..." if len(reflection) > 200 else reflection,
                    "build_result": build_result,
                    "success": build_result["success"]
                }
                
                round_results["agent_actions"].append(action_result)
                
                if build_result["success"]:
                    self.logger.info(f"      ✅ Built tool: {agent.self_built_tools[-1] if agent.self_built_tools else 'unknown'}")
                else:
                    self.logger.info(f"      ❌ Tool building failed")
                    
            except Exception as e:
                self.logger.error(f"      ❌ Error with {agent.agent_id}: {e}")
                
                action_result = {
                    "agent_id": agent.agent_id,
                    "error": str(e),
                    "success": False
                }
                round_results["agent_actions"].append(action_result)
        
        return round_results
    
    def _log_round_summary(self, round_num: int, round_results: Dict[str, Any]):
        """Log summary of the round."""
        
        successful_actions = sum(1 for action in round_results["agent_actions"] if action.get("success", False))
        total_actions = len(round_results["agent_actions"])
        
        self.logger.info(f"   📊 Round {round_num} Summary: {successful_actions}/{total_actions} successful actions")
        
        # Show what tools were built
        for action in round_results["agent_actions"]:
            if action.get("success") and "build_result" in action:
                agent_id = action["agent_id"]
                build_result = action["build_result"]
                if "tool_design" in build_result:
                    tool_info = build_result["tool_design"][:50] + "..."
                    self.logger.info(f"      🔧 {agent_id}: {tool_info}")
    
    def _analyze_experiment_results(self) -> Dict[str, Any]:
        """Analyze final experiment results."""
        
        # Get current tool ecosystem
        all_tools = self.tool_registry.get_all_tools()
        
        # Analyze agent contributions
        agent_contributions = {}
        for agent in self.agents:
            agent_contributions[agent.agent_id] = {
                "tools_built": len(agent.self_built_tools),
                "tool_names": agent.self_built_tools,
                "reflection_count": len(agent.reflection_history)
            }
        
        # Tool type analysis
        tool_types = {}
        personal_tools = 0
        for tool_name, tool_data in all_tools.items():
            if tool_data.get("type") == "personal":
                personal_tools += 1
                
        analysis = {
            "total_tools": len(all_tools),
            "personal_tools_created": personal_tools,
            "shared_tools": len(all_tools) - personal_tools,
            "agent_contributions": agent_contributions,
            "successful_rounds": len([r for r in self.experiment_log if any(a.get("success", False) for a in r.get("agent_actions", []))]),
            "total_rounds": len(self.experiment_log)
        }
        
        return analysis
    
    def _save_experiment_results(self, results: Dict[str, Any]):
        """Save experiment results to files."""
        
        # Save JSON results
        results_file = os.path.join(self.experiment_dir, "results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save experiment metadata
        metadata_file = os.path.join(self.experiment_dir, "experiment_metadata.json")
        metadata = {
            "experiment_name": self.experiment_name,
            "experiment_dir": self.experiment_dir,
            "num_agents": self.num_agents,
            "max_rounds": self.max_rounds,
            "shared_meta_prompt": self.shared_meta_prompt,
            "agent_specializations": self.agent_specializations,
            "directory_structure": {
                "shared_tools": self.shared_tools_dir,
                "personal_tools": self.personal_tools_dir,
                "logs": os.path.join(self.experiment_dir, "experiment.log"),
                "results": results_file,
                "summary": os.path.join(self.experiment_dir, "summary.txt")
            },
            "created_at": results["start_time"],
            "completed_at": results["end_time"]
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save summary
        summary_file = os.path.join(self.experiment_dir, "summary.txt")
        with open(summary_file, 'w') as f:
            f.write(f"EXPERIMENT: {self.experiment_name}\n")
            f.write(f"Directory: {self.experiment_dir}\n")
            f.write(f"Agents: {self.num_agents}\n")
            f.write(f"Rounds: {self.max_rounds}\n")
            f.write(f"Start: {results['start_time']}\n")
            f.write(f"End: {results['end_time']}\n\n")
            
            f.write(f"SPECIALIZATIONS:\n")
            for i, spec in enumerate(self.agent_specializations):
                f.write(f"Agent_{i+1:02d}: {spec}\n")
            f.write(f"\n")
            
            analysis = results["final_analysis"]
            f.write("FINAL ANALYSIS:\n")
            f.write(f"Total tools: {analysis['total_tools']}\n")
            f.write(f"Personal tools created: {analysis['personal_tools_created']}\n")
            f.write(f"Successful rounds: {analysis['successful_rounds']}/{analysis['total_rounds']}\n\n")
            
            f.write("AGENT CONTRIBUTIONS:\n")
            for agent_id, contrib in analysis["agent_contributions"].items():
                f.write(f"{agent_id}: {contrib['tools_built']} tools - {contrib['tool_names']}\n")
            
            f.write(f"\nDIRECTORY STRUCTURE:\n")
            f.write(f"📁 {self.experiment_dir}/\n")
            f.write(f"   📁 shared_tools/     # Shared tools for this experiment\n")
            f.write(f"   📁 personal_tools/   # Agent-created tools\n")
            for i in range(self.num_agents):
                f.write(f"      📁 Agent_{i+1:02d}/\n")
            f.write(f"   📄 experiment.log    # Complete experiment log\n")
            f.write(f"   📄 results.json      # Detailed results\n")
            f.write(f"   📄 summary.txt       # This summary\n")
            f.write(f"   📄 experiment_metadata.json  # Experiment configuration\n")
        
        self.logger.info(f"📁 Complete experiment saved to {self.experiment_dir}")
        self.logger.info(f"   📄 Results: {results_file}")
        self.logger.info(f"   📄 Summary: {summary_file}")
        self.logger.info(f"   📄 Metadata: {metadata_file}")


def main():
    """Run example experiments."""
    
    print("🧬 Agentic Society Experiment Runner")
    print("=" * 50)
    
    # Example 1: Sorting specialists
    print("\n🎯 Example 1: Sorting Specialists Society")
    
    sorting_experiment = ExperimentRunner(
        experiment_name="sorting_specialists",
        num_agents=3,
        max_rounds=5,
        shared_meta_prompt="You are in a collaborative tool-building environment focused on creating high-quality, reusable tools.",
        agent_specializations=[
            "SORTING and ORDERING algorithms",
            "DATA PROCESSING and transformation", 
            "UTILITY and helper functions"
        ]
    )
    
    if sorting_experiment.initialize_experiment():
        results = sorting_experiment.run_experiment()
        print(f"✅ Sorting specialists experiment completed!")
        print(f"📊 Results: {results['final_analysis']['personal_tools_created']} tools created")
    else:
        print("❌ Failed to initialize sorting specialists experiment")
    
    print("\n" + "=" * 50)
    print("🎯 Experiment runner demonstration completed!")


if __name__ == "__main__":
    main() 