#!/usr/bin/env python3
"""
Test script for Agent v1
"""

import sys
import os

# Add src to path
sys.path.append('src')

# Test the agent
if __name__ == "__main__":
    try:
        from src.agent_v1 import main
        main()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc() 