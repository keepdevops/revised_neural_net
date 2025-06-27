#!/usr/bin/env python3
"""
Test animation file detection functionality.
"""

import os
import glob
import sys

def test_animation_file_detection():
    """Test that animation files are detected correctly."""
    print("🧪 Testing animation file detection...")
    
    # Find model directories
    model_dirs = glob.glob("model_*")
    if not model_dirs:
        print("❌ No model directories found")
        return False
    
    # Use the model directory that has animation files
    target_model = "model_20250623_133434"
    if target_model in model_dirs:
        model_dir = target_model
    else:
        # Fallback to most recent
        model_dir = sorted(model_dirs)[-1]
    
    print(f"📁 Using model directory: {model_dir}")
    
    # Check plots directory
    plots_dir = os.path.join(model_dir, 'plots')
    if not os.path.exists(plots_dir):
        print(f"❌ Plots directory does not exist: {plots_dir}")
        return False
    
    print(f"✅ Plots directory exists: {plots_dir}")
    
    # Look for animation files
    animation_files = []
    for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
        files = glob.glob(os.path.join(plots_dir, ext))
        if files:
            print(f"🎬 Found {len(files)} files with extension {ext}:")
            for f in files:
                print(f"   📄 {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
        animation_files.extend(files)
    
    print(f"🎬 Total animation files found: {len(animation_files)}")
    
    if animation_files:
        print("✅ Animation files detected successfully!")
        return True
    else:
        print("❌ No animation files found")
        print("💡 Try running the 3D visualization first to create animation files")
        return False

def test_gradient_descent_script():
    """Test that the gradient descent script creates animation files."""
    print("\n🧪 Testing gradient descent script...")
    
    # Find a model directory
    model_dirs = glob.glob("model_*")
    if not model_dirs:
        print("❌ No model directories found")
        return False
    
    model_dir = sorted(model_dirs)[-1]
    print(f"📁 Using model directory: {model_dir}")
    
    # Check if gradient_descent_3d.py exists
    if not os.path.exists("visualization/gradient_descent_3d.py"):
        print("❌ gradient_descent_3d.py not found")
        return False
    else:
        print("✅ gradient_descent_3d.py found")
    
    # Run the script
    import subprocess
    cmd = [sys.executable, "visualization/gradient_descent_3d.py", "--model_dir", model_dir, "--save_mpeg"]
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Gradient descent script completed successfully")
            
            # Check if animation files were created
            plots_dir = os.path.join(model_dir, 'plots')
            animation_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                animation_files.extend(glob.glob(os.path.join(plots_dir, ext)))
            
            if animation_files:
                print(f"✅ Animation files created: {[os.path.basename(f) for f in animation_files]}")
                return True
            else:
                print("❌ No animation files were created")
                return False
        else:
            print(f"❌ Gradient descent script failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Gradient descent script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running gradient descent script: {e}")
        return False

if __name__ == "__main__":
    print("Testing Animation File Detection")
    print("=" * 50)
    
    # Test 1: Check for existing animation files
    test1_passed = test_animation_file_detection()
    
    # Test 2: Create new animation files
    test2_passed = test_gradient_descent_script()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Animation file detection: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Gradient descent script: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed or test2_passed:
        print("\n✅ Animation file functionality is working!")
    else:
        print("\n❌ Animation file functionality needs attention") 