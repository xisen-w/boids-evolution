"""
Environment Manager - Package and Capability Provider for Agents

Provides agents with information about available packages and capabilities
in their environment, enabling them to build more sophisticated tools.
"""

import os
import json
from typing import Dict, List, Any, Optional


class EnvironmentManager:
    """
    Manages environment information and package availability for agents.
    
    Features:
    - Load available packages from manifest
    - Provide package descriptions and capabilities
    - Format package info for agent consumption
    - Validate package availability
    """
    
    def __init__(self, packages_file: str = "environment/available_packages.json"):
        self.packages_file = packages_file
        self.packages_data = self._load_packages()
        
    def _load_packages(self) -> Dict[str, Any]:
        """Load package information from JSON manifest."""
        if not os.path.exists(self.packages_file):
            print(f"⚠️  Package manifest not found: {self.packages_file}")
            return self._get_default_packages()
        
        try:
            with open(self.packages_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading packages: {e}")
            return self._get_default_packages()
    
    def _get_default_packages(self) -> Dict[str, Any]:
        """Fallback package information if manifest is missing."""
        return {
            "core_packages": {
                "standard_library": {
                    "packages": {
                        "os": "Operating system interface",
                        "json": "JSON data handling",
                        "datetime": "Date and time utilities",
                        "random": "Random number generation",
                        "math": "Mathematical functions"
                    }
                }
            }
        }
    
    def get_package_summary_for_agent(self) -> str:
        """
        Get formatted package summary for agent reflection context.
        
        Returns:
            Formatted string describing available packages
        """
        if not self.packages_data:
            return "📦 AVAILABLE PACKAGES: Basic Python standard library only"
        
        summary_lines = ["📦 AVAILABLE PACKAGES:"]
        summary_lines.append("=" * 50)
        
        # Core packages
        for category, category_data in self.packages_data.get("core_packages", {}).items():
            if isinstance(category_data, dict) and "packages" in category_data:
                desc = category_data.get("description", category.replace("_", " ").title())
                packages = category_data["packages"]
                package_list = ", ".join(list(packages.keys())[:8])  # Limit display
                if len(packages) > 8:
                    package_list += "..."
                summary_lines.append(f"🔧 {desc}: {package_list}")
        
        # AI/LLM packages
        ai_packages = self.packages_data.get("ai_and_llm_packages", {}).get("packages", {})
        if ai_packages:
            ai_list = ", ".join(list(ai_packages.keys())[:6])
            summary_lines.append(f"🤖 AI/LLM: {ai_list}")
            summary_lines.append("   → YOUR OPENAI API KEY IS READY!")
        
        # Search packages
        search_packages = self.packages_data.get("search_and_retrieval", {}).get("packages", {})
        if search_packages:
            search_list = ", ".join(list(search_packages.keys())[:5])
            summary_lines.append(f"🔍 Search: {search_list}")
            summary_lines.append("   → YOUR TAVILY API KEY IS READY FOR WEB SEARCH!")
        
        # Visualization packages
        viz_packages = self.packages_data.get("visualization", {}).get("packages", {})
        if viz_packages:
            summary_lines.append(f"📊 Visualization: {', '.join(viz_packages.keys())}")
        
        # Text processing packages
        text_packages = self.packages_data.get("text_processing", {}).get("packages", {})
        if text_packages:
            summary_lines.append(f"📝 Text Processing: {', '.join(text_packages.keys())}")
        
        # Add capabilities section
        capabilities = self.packages_data.get("agent_capabilities", {}).get("examples", [])
        if capabilities:
            summary_lines.append("")
            summary_lines.append("🎯 WHAT YOU CAN BUILD:")
            for capability in capabilities[:8]:  # Show first 8 examples
                summary_lines.append(f"  • {capability}")
            if len(capabilities) > 8:
                summary_lines.append("  • ...and much more!")
        
        return "\n".join(summary_lines)
    
    def get_package_details(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific package."""
        for category_name, category_data in self.packages_data.items():
            if isinstance(category_data, dict) and "packages" in category_data:
                packages = category_data["packages"]
                if package_name in packages:
                    return {
                        "name": package_name,
                        "description": packages[package_name],
                        "category": category_data.get("description", category_name)
                    }
        return None
    
    def get_all_available_packages(self) -> List[str]:
        """Get list of all available package names."""
        all_packages = []
        
        for category_data in self.packages_data.values():
            if isinstance(category_data, dict) and "packages" in category_data:
                all_packages.extend(category_data["packages"].keys())
        
        return sorted(all_packages)
    
    def get_import_examples(self) -> List[str]:
        """Get example import statements for common packages."""
        return self.packages_data.get("usage_guidelines", {}).get("import_examples", [])
    
    def get_best_practices(self) -> List[str]:
        """Get coding best practices for tool building."""
        return self.packages_data.get("usage_guidelines", {}).get("best_practices", [])
    
    def validate_package_usage(self, code: str) -> Dict[str, Any]:
        """
        Validate if code uses only available packages.
        
        Args:
            code: Python code to validate
            
        Returns:
            Validation results with used packages and availability
        """
        import re
        
        # Built-in Python modules that are always available
        builtin_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'random', 'math', 're', 'collections',
            'itertools', 'functools', 'operator', 'string', 'io', 'base64', 'hashlib',
            'urllib', 'http', 'socket', 'threading', 'multiprocessing', 'subprocess',
            'pathlib', 'tempfile', 'shutil', 'glob', 'fnmatch', 'csv', 'xml', 'html',
            'sqlite3', 'pickle', 'copy', 'types', 'inspect', 'traceback', 'logging',
            'warnings', 'contextlib', 'abc', 'enum', 'dataclasses', 'typing'
        }
        
        # HARDCODED: Critical packages that must be available (Fix 5)
        hardcoded_available = {
            'pandas', 'numpy', 'sklearn', 'scikit-learn', 'matplotlib', 'seaborn',
            'PyPDF2', 'pdfplumber', 'requests', 'openai', 'tavily', 'anthropic',
            'beautifulsoup4', 'plotly', 'scipy', 'nltk', 'transformers', 'langchain'
        }
        
        # Extract import statements - handle both 'import pkg' and 'from pkg import ...'
        used_packages = set()
        
        # Find 'import package' statements
        import_matches = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', code, re.MULTILINE)
        for pkg in import_matches:
            base_pkg = pkg.split('.')[0]
            if base_pkg not in builtin_modules:
                used_packages.add(base_pkg)
        
        # Find 'from package import ...' statements
        from_matches = re.findall(r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import', code, re.MULTILINE)
        for pkg in from_matches:
            base_pkg = pkg.split('.')[0]
            if base_pkg not in builtin_modules:
                used_packages.add(base_pkg)
        
        available_packages = set(self.get_all_available_packages()) | hardcoded_available
        
        return {
            "used_packages": list(used_packages),
            "available_packages": list(available_packages),
            "valid_packages": list(used_packages & available_packages),
            "invalid_packages": list(used_packages - available_packages),
            "all_valid": len(used_packages - available_packages) == 0
        }


def main():
    """Test the Environment Manager."""
    print("🧪 Testing Environment Manager")
    print("=" * 50)
    
    # Test loading
    env_manager = EnvironmentManager()
    print("✅ Environment Manager initialized")
    
    # Test package summary
    print("\n📦 Package Summary for Agent:")
    print(env_manager.get_package_summary_for_agent())
    
    # Test package details
    print("\n🔍 Package Details (pandas):")
    details = env_manager.get_package_details("pandas")
    if details:
        print(f"   Name: {details['name']}")
        print(f"   Description: {details['description']}")
        print(f"   Category: {details['category']}")
    
    # Test import examples
    print("\n📝 Import Examples:")
    for example in env_manager.get_import_examples():
        print(f"   {example}")
    
    # Test validation
    print("\n🔧 Code Validation Test:")
    test_code = """
import pandas as pd
import numpy as np
import requests
import openai
import some_unknown_package
"""
    validation = env_manager.validate_package_usage(test_code)
    print(f"   Used packages: {validation['used_packages']}")
    print(f"   Valid: {validation['valid_packages']}")
    print(f"   Invalid: {validation['invalid_packages']}")
    print(f"   All valid: {validation['all_valid']}")


if __name__ == "__main__":
    main() 