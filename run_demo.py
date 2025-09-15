#!/usr/bin/env python3
"""
Quick Demo Runner for Boids Evolution Visualization
==================================================

This script provides an easy way to run the visualization demo
with different options and handles dependency checking.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'matplotlib',
        'networkx', 
        'plotly',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Install with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ All dependencies satisfied!")
    return True

def find_experiment_directory():
    """Find the most recent experiment directory."""
    experiments_dir = Path('experiments')
    
    if not experiments_dir.exists():
        print("❌ No experiments directory found")
        return None
    
    # Find all experiment directories
    exp_dirs = [d for d in experiments_dir.iterdir() if d.is_dir()]
    
    if not exp_dirs:
        print("❌ No experiment directories found")
        return None
    
    # Get the most recent one
    most_recent = max(exp_dirs, key=lambda d: d.stat().st_mtime)
    print(f"📁 Found most recent experiment: {most_recent.name}")
    
    return most_recent

def run_demo(demo_type='all'):
    """Run the visualization demo."""
    print("🎨 Boids Evolution Visualization Demo")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Find experiment directory
    exp_dir = find_experiment_directory()
    if not exp_dir:
        print("⚠️  No experiment data found - will generate synthetic demo data")
        exp_dir = "demo"  # Will trigger synthetic data generation
    
    # Create visualizations directory
    vis_dir = Path('visualizations')
    vis_dir.mkdir(exist_ok=True)
    
    # Run the visualizer
    cmd = [
        sys.executable, 
        'demo_visualizer.py',
        '--experiment-dir', str(exp_dir),
        '--output-dir', str(vis_dir)
    ]
    
    if demo_type == 'animation':
        cmd.append('--animation')
    elif demo_type == 'dashboard':
        cmd.append('--dashboard')
    elif demo_type == 'report':
        cmd.append('--report')
    else:
        cmd.append('--all')
    
    print(f"\n🚀 Running visualization...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        
        print("\n🎉 Demo completed successfully!")
        print(f"📂 Check the 'visualizations' directory for output files")
        
        # List created files
        if vis_dir.exists():
            files = list(vis_dir.glob('*'))
            if files:
                print("\n📄 Created files:")
                for file in files:
                    print(f"  - {file.name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running demo: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ demo_visualizer.py not found - make sure you're in the right directory")
        return False

def main():
    """Main function with simple menu."""
    print("🧬 Boids Evolution Visualization Demo")
    print("=====================================")
    print()
    print("Choose visualization type:")
    print("1. 🎬 Animated Network (GIF)")
    print("2. 🎛️ Interactive Dashboard (HTML)")
    print("3. 📊 Summary Report (HTML)")
    print("4. 🎨 All Visualizations")
    print("5. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                return run_demo('animation')
            elif choice == '2':
                return run_demo('dashboard')
            elif choice == '3':
                return run_demo('report')
            elif choice == '4':
                return run_demo('all')
            elif choice == '5':
                print("👋 Goodbye!")
                return True
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return True
        except EOFError:
            print("\n👋 Goodbye!")
            return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

