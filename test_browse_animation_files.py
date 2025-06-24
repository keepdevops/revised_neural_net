#!/usr/bin/env python3
"""
Test script to verify the directory browsing functionality for animation files.
"""

import os
import sys
import glob
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_directory_browsing_logic():
    """Test the directory browsing logic for finding animation files."""
    print("🔍 Testing Directory Browsing Logic for Animation Files")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Model Directory with Plots",
            "selected_dir": "model_20250623_112543",
            "expected_plots": "model_20250623_112543/plots"
        },
        {
            "name": "Plots Directory Direct",
            "selected_dir": "model_20250623_112543/plots",
            "expected_plots": "model_20250623_112543/plots"
        },
        {
            "name": "Directory with Animation Files",
            "selected_dir": "model_20250623_112818/plots",
            "expected_plots": "model_20250623_112818/plots"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📁 Testing: {scenario['name']}")
        print(f"   Selected directory: {scenario['selected_dir']}")
        
        # Simulate the logic from browse_mpeg_files
        selected_dir = scenario['selected_dir']
        
        # Check if the selected directory is a plots subdirectory
        if os.path.basename(selected_dir) == 'plots':
            plots_path = selected_dir
            print(f"   ✅ User selected plots directory directly: {plots_path}")
        else:
            # Check if it's a model directory with a plots subdirectory
            plots_path = os.path.join(selected_dir, 'plots')
            if os.path.exists(plots_path):
                print(f"   ✅ Found plots subdirectory in model: {plots_path}")
            else:
                # Check if the selected directory itself contains animation files
                plots_path = selected_dir
                print(f"   🔍 Checking selected directory for animation files: {plots_path}")
        
        # Verify the expected plots path
        if plots_path == scenario['expected_plots']:
            print(f"   ✅ Correct plots path determined: {plots_path}")
        else:
            print(f"   ❌ Incorrect plots path: {plots_path} (expected: {scenario['expected_plots']})")
        
        # Check if directory exists
        if os.path.exists(plots_path):
            print(f"   ✅ Directory exists: {plots_path}")
            
            # Look for animation files
            animation_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                files = glob.glob(os.path.join(plots_path, ext))
                if files:
                    print(f"   🎬 Found {len(files)} files with extension {ext}:")
                    for f in files:
                        print(f"      📄 {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
                animation_files.extend(files)
            
            print(f"   🎬 Total animation files found: {len(animation_files)}")
            
            if animation_files:
                print(f"   ✅ Animation files found successfully!")
            else:
                print(f"   ⚠️  No animation files found in this directory")
        else:
            print(f"   ❌ Directory does not exist: {plots_path}")

def test_available_animation_files():
    """Test to show all available animation files in the project."""
    print("\n🎬 Available Animation Files in Project")
    print("=" * 60)
    
    # Find all model directories
    model_dirs = []
    for item in os.listdir(project_root):
        if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
            model_dirs.append(item)
    
    print(f"Found {len(model_dirs)} model directories")
    
    total_animation_files = 0
    
    for model_dir in model_dirs:
        plots_path = os.path.join(model_dir, 'plots')
        if os.path.exists(plots_path):
            animation_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                files = glob.glob(os.path.join(plots_path, ext))
                animation_files.extend(files)
            
            if animation_files:
                print(f"\n📁 {model_dir}/plots:")
                for file_path in animation_files:
                    file_size = os.path.getsize(file_path)
                    print(f"   🎬 {os.path.basename(file_path)} ({file_size:,} bytes)")
                total_animation_files += len(animation_files)
    
    print(f"\n🎬 Total animation files found: {total_animation_files}")
    
    if total_animation_files > 0:
        print("\n✅ Directory browsing should work! Users can:")
        print("   1. Click 'Browse' in Plot Controls tab")
        print("   2. Navigate to any model directory (e.g., model_20250623_112543)")
        print("   3. Select the 'plots' subdirectory")
        print("   4. Find and open animation files")
    else:
        print("\n❌ No animation files found. Users need to create 3D visualizations first.")

if __name__ == "__main__":
    test_directory_browsing_logic()
    test_available_animation_files() 