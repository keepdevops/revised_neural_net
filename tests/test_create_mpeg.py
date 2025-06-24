#!/usr/bin/env python3
"""
Test script to create an MPEG file using the 3D visualization script.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_mpeg():
    """Create a test MPEG file using the 3D visualization script."""
    print("Creating test MPEG file...")
    
    # Find a model directory with training data
    model_dirs = []
    for item in os.listdir(project_root):
        if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
            # Check if it has training losses
            loss_file = os.path.join(project_root, item, 'training_losses.csv')
            if os.path.exists(loss_file):
                model_dirs.append(item)
    
    if not model_dirs:
        print("❌ No model directories with training data found")
        return False
    
    # Use the first model with training data
    test_model = os.path.join(project_root, model_dirs[0])
    print(f"Using model: {test_model}")
    
    # Check if MPEG file already exists
    mpeg_files = []
    for ext in ['*.mpeg', '*.mpg', '*.mp4']:
        mpeg_files.extend(glob.glob(os.path.join(test_model, ext)))
    
    if mpeg_files:
        print(f"✅ MPEG file already exists: {os.path.basename(mpeg_files[0])}")
        return True
    
    # Create MPEG file using the 3D visualization script
    script_path = os.path.join(project_root, 'gradient_descent_3d.py')
    
    cmd = [
        sys.executable, script_path,
        '--model_dir', test_model,
        '--color', 'viridis',
        '--point_size', '50',
        '--line_width', '2',
        '--surface_alpha', '0.3',
        '--w1_range', '-2.0', '2.0',
        '--w2_range', '-2.0', '2.0',
        '--n_points', '20',
        '--view_elev', '30',
        '--view_azim', '45',
        '--fps', '30',
        '--w1_index', '0',
        '--w2_index', '1',
        '--output_resolution', '800', '600',
        '--save_mpeg'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"stdout: {result.stdout}")
        if result.stderr:
            print(f"stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Check if MPEG file was created
            mpeg_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4']:
                mpeg_files.extend(glob.glob(os.path.join(test_model, ext)))
            
            if mpeg_files:
                print(f"✅ MPEG file created successfully: {os.path.basename(mpeg_files[0])}")
                file_size = os.path.getsize(mpeg_files[0])
                print(f"   File size: {file_size} bytes")
                return True
            else:
                print("❌ MPEG file was not created")
                return False
        else:
            print("❌ Script failed to create MPEG file")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def main():
    """Run the MPEG creation test."""
    print("MPEG Creation Test")
    print("=" * 30)
    
    success = create_test_mpeg()
    
    if success:
        print("\n🎉 MPEG file creation test passed!")
        print("You can now use the GUI to:")
        print("1. Select a model in the Model Management tab")
        print("2. Go to the Plot Controls tab")
        print("3. Use the MPEG Animation Files section to browse and open MPEG files")
    else:
        print("\n❌ MPEG file creation test failed!")
    
    return success

if __name__ == "__main__":
    import glob
    success = main()
    sys.exit(0 if success else 1) 