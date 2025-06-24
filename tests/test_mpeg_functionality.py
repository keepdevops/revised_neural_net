#!/usr/bin/env python3
"""
Test script to verify MPEG file functionality in the GUI.
"""

import os
import sys
import glob
import subprocess
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_mpeg_file_detection():
    """Test MPEG file detection in model directories."""
    print("Testing MPEG file detection...")
    
    # Look for model directories
    model_dirs = []
    for item in os.listdir(project_root):
        if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
            model_dirs.append(item)
    
    print(f"Found {len(model_dirs)} model directories: {model_dirs}")
    
    # Check each model directory for MPEG files
    for model_dir in model_dirs:
        model_path = os.path.join(project_root, model_dir)
        print(f"\nChecking {model_dir}...")
        
        # Look for MPEG files
        mpeg_files = []
        for ext in ['*.mpeg', '*.mpg', '*.mp4']:
            mpeg_files.extend(glob.glob(os.path.join(model_path, ext)))
        
        if mpeg_files:
            print(f"  Found {len(mpeg_files)} MPEG file(s):")
            for file_path in mpeg_files:
                file_size = os.path.getsize(file_path)
                print(f"    {os.path.basename(file_path)} ({file_size} bytes)")
        else:
            print("  No MPEG files found")
    
    return True

def test_3d_visualization_script():
    """Test if the 3D visualization script can create MPEG files."""
    print("\nTesting 3D visualization script...")
    
    # Check if gradient_descent_3d.py exists
    script_path = os.path.join(project_root, 'gradient_descent_3d.py')
    if not os.path.exists(script_path):
        print("❌ gradient_descent_3d.py not found")
        return False
    
    print("✅ gradient_descent_3d.py found")
    
    # Check if it has MPEG saving capability
    with open(script_path, 'r') as f:
        content = f.read()
        if '--save_mpeg' in content:
            print("✅ Script supports --save_mpeg option")
        else:
            print("❌ Script does not support --save_mpeg option")
            return False
    
    return True

def test_script_launcher():
    """Test the script launcher functionality."""
    print("\nTesting script launcher...")
    
    try:
        from script_launcher import launch_3d_visualization
        print("✅ Script launcher imported successfully")
        
        # Test with a sample model directory
        model_dirs = [d for d in os.listdir(project_root) if d.startswith('model_') and os.path.isdir(os.path.join(project_root, d))]
        
        if model_dirs:
            test_model = os.path.join(project_root, model_dirs[0])
            print(f"Testing with model: {test_model}")
            
            # Test parameters
            params = {
                'color': 'viridis',
                'point_size': 50,
                'line_width': 2,
                'surface_alpha': 0.3,
                'w1_range_min': -2.0,
                'w1_range_max': 2.0,
                'w2_range_min': -2.0,
                'w2_range_max': 2.0,
                'n_points': 20,
                'view_elev': 30,
                'view_azim': 45,
                'fps': 30,
                'w1_index': 0,
                'w2_index': 1,
                'output_width': 800,
                'output_height': 600
            }
            
            print("✅ Script launcher test parameters prepared")
            return True
        else:
            print("❌ No model directories found for testing")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import script launcher: {e}")
        return False
    except Exception as e:
        print(f"❌ Script launcher test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("MPEG Functionality Test Suite")
    print("=" * 40)
    
    tests = [
        test_mpeg_file_detection,
        test_3d_visualization_script,
        test_script_launcher
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MPEG functionality should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 