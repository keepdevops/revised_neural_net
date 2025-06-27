#!/usr/bin/env python3
"""
Test MPEG generation functionality.
"""

import os
import sys
import subprocess
import glob
import tempfile
import shutil

def test_mpeg_generation():
    """Test that MPEG generation works correctly."""
    print("🧪 Testing MPEG generation functionality...")
    
    # Check if gradient_descent_3d.py exists
    if not os.path.exists("visualization/gradient_descent_3d.py"):
        print("❌ gradient_descent_3d.py not found")
        return False
    
    print("✅ gradient_descent_3d.py found")
    
    # Create a temporary model directory with mock data
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Created temporary directory: {temp_dir}")
        
        # Create mock training losses
        import numpy as np
        losses = np.random.random(100) * 0.1  # 100 random losses
        loss_file = os.path.join(temp_dir, 'training_losses.csv')
        np.savetxt(loss_file, losses, delimiter=',')
        
        # Create mock weight history files
        weights_dir = os.path.join(temp_dir, 'weights_history')
        os.makedirs(weights_dir, exist_ok=True)
        
        for i in range(10):
            weights = np.random.random(2)  # 2 weights
            weight_file = os.path.join(weights_dir, f'weights_history_{i:04d}.csv')
            np.savetxt(weight_file, weights, delimiter=',')
        
        # Create plots directory
        plots_dir = os.path.join(temp_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        print("📊 Created mock training data")
        
        # Test MPEG generation
        cmd = [sys.executable, "visualization/gradient_descent_3d.py", "--model_dir", temp_dir, "--save_mpeg"]
        print(f"🎬 Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ MPEG generation completed successfully")
                
                # Check for generated files
                mpeg_files = glob.glob(os.path.join(plots_dir, "*.mp4"))
                gif_files = glob.glob(os.path.join(plots_dir, "*.gif"))
                png_files = glob.glob(os.path.join(plots_dir, "gradient_descent_3d_frame_*.png"))
                
                print(f"📁 Generated files:")
                print(f"   - MP4 files: {len(mpeg_files)}")
                print(f"   - GIF files: {len(gif_files)}")
                print(f"   - PNG frames: {len(png_files)}")
                
                if mpeg_files or gif_files:
                    print("✅ Animation files generated successfully")
                    return True
                else:
                    print("⚠️  No animation files found")
                    return False
            else:
                print(f"❌ MPEG generation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ MPEG generation timed out")
            return False
        except Exception as e:
            print(f"❌ MPEG generation error: {e}")
            return False

def test_gui_mpeg_methods():
    """Test that the GUI MPEG methods exist and are callable."""
    print("\n🧪 Testing GUI MPEG methods...")
    
    try:
        # Import the GUI module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gui.main_gui import StockPredictionGUI
        
        # Check if the methods exist
        methods_to_check = [
            'generate_mpeg_animation',
            '_mpeg_generation_completed_success',
            '_mpeg_generation_completed_error',
            'refresh_mpeg_files',
            'browse_mpeg_files',
            'open_selected_mpeg'
        ]
        
        for method_name in methods_to_check:
            if hasattr(StockPredictionGUI, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        print("✅ All GUI MPEG methods exist")
        return True
        
    except Exception as e:
        print(f"❌ Error testing GUI methods: {e}")
        return False

def main():
    """Run all MPEG generation tests."""
    print("🎬 MPEG Generation Test Suite")
    print("=" * 50)
    
    # Test 1: MPEG generation functionality
    test1_passed = test_mpeg_generation()
    
    # Test 2: GUI methods
    test2_passed = test_gui_mpeg_methods()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   - MPEG Generation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   - GUI Methods: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! MPEG generation is working correctly.")
        return True
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 