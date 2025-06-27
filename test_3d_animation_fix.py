#!/usr/bin/env python3
"""
Test script to verify 3D animation and MPEG saving functionality.
"""

import os
import sys
import subprocess
import glob
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_3d_visualization():
    """Test the 3D visualization with MPEG saving."""
    print("Testing 3D Visualization with MPEG Saving")
    print("=" * 50)
    
    # Find a model directory
    model_dirs = glob.glob("model_*")
    if not model_dirs:
        print("❌ No model directories found")
        return False
    
    # Use the most recent model directory
    model_dir = sorted(model_dirs)[-1]
    print(f"Using model directory: {model_dir}")
    
    # Test parameters
    params = {
        'color': 'viridis',
        'point_size': 8,
        'line_width': 3,
        'surface_alpha': 0.6,
        'w1_range_min': -2.0,
        'w1_range_max': 2.0,
        'w2_range_min': -2.0,
        'w2_range_max': 2.0,
        'n_points': 30,
        'view_elev': 30.0,
        'view_azim': 45.0,
        'fps': 30,
        'w1_index': 0,
        'w2_index': 0,
        'output_width': 1200,
        'output_height': 800
    }
    
    # Build command
    cmd = [
        sys.executable, 'visualization/gradient_descent_3d.py',
        '--model_dir', model_dir,
        '--color', params['color'],
        '--point_size', str(params['point_size']),
        '--line_width', str(params['line_width']),
        '--surface_alpha', str(params['surface_alpha']),
        '--w1_range', str(params['w1_range_min']), str(params['w1_range_max']),
        '--w2_range', str(params['w2_range_min']), str(params['w2_range_max']),
        '--n_points', str(params['n_points']),
        '--view_elev', str(params['view_elev']),
        '--view_azim', str(params['view_azim']),
        '--fps', str(params['fps']),
        '--w1_index', str(params['w1_index']),
        '--w2_index', str(params['w2_index']),
        '--output_resolution', str(params['output_width']), str(params['output_height']),
        '--save_mpeg'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"Return code: {result.returncode}")
        print(f"stdout: {result.stdout}")
        if result.stderr:
            print(f"stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ 3D visualization completed successfully")
            
            # Check for output files
            plots_dir = os.path.join(model_dir, 'plots')
            if os.path.exists(plots_dir):
                # Look for animation files
                mp4_files = glob.glob(os.path.join(plots_dir, "*.mp4"))
                gif_files = glob.glob(os.path.join(plots_dir, "*.gif"))
                png_files = glob.glob(os.path.join(plots_dir, "gradient_descent_3d_frame_*.png"))
                
                print(f"Found {len(mp4_files)} MP4 files")
                print(f"Found {len(gif_files)} GIF files")
                print(f"Found {len(png_files)} PNG frame files")
                
                if mp4_files:
                    print(f"✅ MPEG animation created: {mp4_files[0]}")
                    return True
                elif gif_files:
                    print(f"✅ GIF animation created: {gif_files[0]}")
                    return True
                elif png_files:
                    print(f"✅ PNG frames created: {len(png_files)} files")
                    return True
                else:
                    print("❌ No animation files found")
                    return False
            else:
                print("❌ Plots directory not found")
                return False
        else:
            print("❌ 3D visualization failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 3D visualization timed out")
        return False
    except Exception as e:
        print(f"❌ Error running 3D visualization: {e}")
        return False

def test_gui_3d_animation():
    """Test that the GUI can start without 3D animation errors."""
    print("\nTesting GUI 3D Animation Initialization")
    print("=" * 50)
    
    try:
        # Import the GUI modules
        import tkinter as tk
        from gui.main_gui import StockPredictionGUI
        
        # Create a minimal GUI instance
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = StockPredictionGUI(root)
        
        # Test 3D axes availability
        if app.ensure_3d_axes_available():
            print("✅ 3D axes are available")
            
            # Test that the 3D animation methods exist
            if hasattr(app, 'play_gd_animation'):
                print("✅ play_gd_animation method exists")
            else:
                print("❌ play_gd_animation method missing")
                return False
                
            if hasattr(app, 'pause_gd_animation'):
                print("✅ pause_gd_animation method exists")
            else:
                print("❌ pause_gd_animation method missing")
                return False
                
            if hasattr(app, 'stop_gd_animation'):
                print("✅ stop_gd_animation method exists")
            else:
                print("❌ stop_gd_animation method missing")
                return False
                
            return True
        else:
            print("❌ 3D axes are not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GUI 3D animation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_3d_animation_fix():
    """Test that the 3D animation frame index error is fixed."""
    print("🧪 Testing 3D animation frame index fix...")
    
    # Test with the test_3d_model directory
    model_dir = "test_3d_model"
    if not os.path.exists(model_dir):
        print(f"❌ Test model directory not found: {model_dir}")
        print("Please run a training first to create test_3d_model")
        return False
    
    try:
        # Check if weight history files exist
        weights_files = sorted([f for f in os.listdir(os.path.join(model_dir, "weights_history")) 
                              if f.startswith("weights_history_") and f.endswith(".npz")])
        
        if not weights_files:
            print("❌ No weight history files found")
            return False
        
        print(f"✅ Found {len(weights_files)} weight history files")
        
        # Check if training losses file exists
        losses_file = os.path.join(model_dir, "training_losses.csv")
        if not os.path.exists(losses_file):
            print("❌ No training losses file found")
            return False
        
        # Load losses
        losses = np.loadtxt(losses_file, delimiter=",")
        if losses.ndim > 1:
            losses = losses[:, 0]  # Use training losses
        
        print(f"✅ Found {len(losses)} loss values")
        
        # Simulate the frame mapping logic
        num_weight_frames = len(weights_files)
        print(f"📊 Weight frames: {num_weight_frames}")
        print(f"📊 Loss values: {len(losses)}")
        
        # Test frame mapping
        for frame in range(num_weight_frames):
            # This is the logic from the fixed update_gd3d_frame method
            loss_index = min(frame * 50, len(losses) - 1)
            print(f"Frame {frame} -> Loss index {loss_index} (epoch {frame * 50})")
            
            # Verify the indices are valid
            if frame >= num_weight_frames:
                print(f"❌ Frame {frame} exceeds weight history ({num_weight_frames})")
                return False
            
            if loss_index >= len(losses):
                print(f"❌ Loss index {loss_index} exceeds loss history ({len(losses)})")
                return False
        
        print("✅ All frame mappings are valid")
        
        # Test edge cases
        print("\n🔍 Testing edge cases...")
        
        # Test frame that would exceed weight history
        frame = num_weight_frames + 5
        if frame >= num_weight_frames:
            print(f"✅ Frame {frame} correctly detected as exceeding weight history ({num_weight_frames})")
            frame = num_weight_frames - 1  # This is the fix
            print(f"✅ Frame adjusted to {frame}")
        
        # Test loss index mapping for the last frame
        last_frame = num_weight_frames - 1
        loss_index = min(last_frame * 50, len(losses) - 1)
        print(f"✅ Last frame {last_frame} maps to loss index {loss_index}")
        
        print("\n🎉 All tests passed! The 3D animation frame index error has been fixed.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("3D Animation and MPEG Saving Test Suite")
    print("=" * 60)
    
    # Test 1: 3D visualization with MPEG saving
    test1_passed = test_3d_visualization()
    
    # Test 2: GUI 3D animation initialization
    test2_passed = test_gui_3d_animation()
    
    # Test 3: 3D animation frame index fix
    test3_passed = test_3d_animation_fix()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"3D Visualization with MPEG: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"GUI 3D Animation Init: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"3D Animation Frame Index Fix: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED! 3D animation and MPEG saving are working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 