#!/usr/bin/env python3
"""
Test script to verify debug messages for animation file browsing.
"""

import os
import sys
import glob

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_debug_messages():
    """Test the debug messages for animation file browsing."""
    print("🔍 Testing Debug Messages for Animation File Browsing")
    print("=" * 60)
    
    # Test with a model that has animation files
    model_with_animations = "model_20250623_112543"
    plots_path = os.path.join(model_with_animations, 'plots')
    
    print(f"📁 Testing with model: {model_with_animations}")
    print(f"📂 Plots directory: {plots_path}")
    
    if os.path.exists(plots_path):
        print(f"✅ Plots directory exists")
        existing_files = os.listdir(plots_path)
        print(f"📋 Existing files in plots directory: {existing_files}")
        
        # Look for animation files
        animation_files = []
        for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
            animation_files.extend(glob.glob(os.path.join(plots_path, ext)))
        
        print(f"🎬 Animation files found: {[os.path.basename(f) for f in animation_files]}")
        
        if animation_files:
            print(f"✅ Found {len(animation_files)} animation file(s)")
            for file in animation_files:
                size = os.path.getsize(file)
                print(f"   📄 {os.path.basename(file)} ({size:,} bytes)")
        else:
            print(f"❌ No animation files found")
    else:
        print(f"❌ Plots directory does not exist")
    
    print("\n🎬 To test in the GUI:")
    print("1. Start the GUI: python gui/main_gui.py")
    print("2. Select model: model_20250623_112543")
    print("3. Go to Plot Controls tab")
    print("4. Click 'Browse MPEG Files'")
    print("5. You should see the debug messages and animation files")

if __name__ == "__main__":
    test_debug_messages() 