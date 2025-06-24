#!/usr/bin/env python3
"""
Test script to verify that the GUI can find and handle existing animation files.
"""

import os
import sys
import glob
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_animation_file_detection():
    """Test if the GUI can detect existing animation files."""
    print("Testing animation file detection...")
    
    # Look for model directories
    model_dirs = []
    for item in os.listdir(project_root):
        if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
            model_dirs.append(item)
    
    print(f"Found {len(model_dirs)} model directories")
    
    # Check each model directory for animation files
    total_animation_files = 0
    for model_dir in model_dirs:
        model_path = os.path.join(project_root, model_dir)
        plots_path = os.path.join(model_path, 'plots')
        
        # Check if plots directory exists
        if not os.path.exists(plots_path):
            print(f"\n📁 {model_dir}: No plots directory found")
            continue
        
        # Look for animation files in plots directory
        animation_files = []
        for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
            animation_files.extend(glob.glob(os.path.join(plots_path, ext)))
        
        if animation_files:
            print(f"\n📁 {model_dir}/plots:")
            for file_path in animation_files:
                file_size = os.path.getsize(file_path)
                print(f"  ✅ {os.path.basename(file_path)} ({file_size:,} bytes)")
                total_animation_files += 1
        else:
            print(f"\n📁 {model_dir}/plots: No animation files found")
    
    print(f"\n🎬 Total animation files found: {total_animation_files}")
    return total_animation_files > 0

def main():
    """Run all tests."""
    print("GUI Animation Files Test Suite")
    print("=" * 40)
    
    tests = [
        test_animation_file_detection
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
        print("🎉 All tests passed! The GUI should be able to find and display animation files.")
        print("\nTo use the animation files in the GUI:")
        print("1. Start the GUI: python gui/main_gui.py")
        print("2. Select a model in the Model Management tab")
        print("3. Go to the Plot Controls tab")
        print("4. Use the 'Animation Files (MPEG/GIF/MP4)' section")
        print("5. Click 'Browse MPEG Files' or 'Refresh List'")
        print("6. Select an animation file and click 'Open Selected'")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 