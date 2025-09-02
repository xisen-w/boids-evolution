#!/usr/bin/env python3
"""
Test Enhanced Environment Management System
"""

import sys
import os

# Add src to path
sys.path.append('src')

def test_environment_manager():
    """Test the environment manager functionality."""
    print("🧪 TESTING ENHANCED ENVIRONMENT MANAGEMENT")
    print("=" * 60)
    
    try:
        from environment_manager import EnvironmentManager
        
        # Initialize environment manager
        env_manager = EnvironmentManager()
        print("✅ Environment Manager initialized successfully")
        
        # Test package summary for agent
        print("\n📦 PACKAGE SUMMARY FOR AGENTS:")
        print("-" * 40)
        summary = env_manager.get_package_summary_for_agent()
        print(summary)
        
        # Test package details
        print("\n🔍 PACKAGE DETAILS EXAMPLES:")
        print("-" * 40)
        test_packages = ["openai", "pandas", "requests", "tavily"]
        for pkg in test_packages:
            details = env_manager.get_package_details(pkg)
            if details:
                print(f"• {details['name']}: {details['description']}")
        
        # Test code validation
        print("\n🔧 CODE VALIDATION TEST:")
        print("-" * 40)
        test_code = """
import pandas as pd
import numpy as np
import requests
from openai import OpenAI
import tavily
import some_unknown_package
"""
        validation = env_manager.validate_package_usage(test_code)
        print(f"Used packages: {validation['used_packages']}")
        print(f"✅ Valid packages: {validation['valid_packages']}")
        print(f"❌ Invalid packages: {validation['invalid_packages']}")
        print(f"All valid: {'✅ YES' if validation['all_valid'] else '❌ NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing environment manager: {e}")
        return False

def test_agent_integration():
    """Test agent integration with environment manager."""
    print("\n\n🤖 TESTING AGENT INTEGRATION")
    print("=" * 60)
    
    try:
        # Mock agent class for testing
        class MockAgent:
            def __init__(self):
                from environment_manager import EnvironmentManager
                self.environment_manager = EnvironmentManager()
                self.agent_id = "TestAgent"
                self.meta_prompt = "Focus on data analysis tools"
                self.envs_available = ["python", "data_processing", "ai_tools"]
            
            def get_enhanced_system_prompt(self):
                """Test the enhanced system prompt with package info."""
                package_info = ""
                if self.environment_manager:
                    package_info = f"\n\n{self.environment_manager.get_package_summary_for_agent()}"
                
                return f"""You are Agent {self.agent_id} in a tool-building ecosystem.

META CONTEXT: {self.meta_prompt}

AVAILABLE ENVIRONMENTS: {', '.join(self.envs_available)}{package_info}

Reflect on the current tool ecosystem and think strategically about what to build next."""
        
        # Test mock agent
        agent = MockAgent()
        print("✅ Mock agent created with environment manager")
        
        # Test enhanced prompt
        print("\n📝 ENHANCED AGENT SYSTEM PROMPT:")
        print("-" * 40)
        prompt = agent.get_enhanced_system_prompt()
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent integration: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 ENHANCED ENVIRONMENT SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Test 1: Environment Manager
    test1_passed = test_environment_manager()
    
    # Test 2: Agent Integration
    test2_passed = test_agent_integration()
    
    # Summary
    print("\n\n📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Environment Manager: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Agent Integration: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🎯 NEXT STEPS:")
        print("1. Run: chmod +x environment/setup_venv.sh")
        print("2. Run: ./environment/setup_venv.sh")
        print("3. Set up your API keys in .env file")
        print("4. Run enhanced experiments!")
    else:
        print("\n⚠️ SOME TESTS FAILED - CHECK ERRORS ABOVE")

if __name__ == "__main__":
    main() 