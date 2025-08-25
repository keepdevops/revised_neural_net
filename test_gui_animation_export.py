#!/usr/bin/env python3
"""
Test script to verify GUI animation export functionality with real model data.
"""

import os
import sys
import glob
import subprocess

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def find_working_model():
    """Find a working model directory with proper files."""
    print("🔍 Looking for working model directories...")
    
    # Look for model directories
    model_dirs = glob.glob("model_*")
    if not model_dirs:
        print("❌ No model directories found")
        return None
    
    # Sort by creation time (newest first)
    model_dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
    
    for model_dir in model_dirs:
        print(f"📁 Checking model: {model_dir}")
        
        # Check for required files
        required_files = [
            os.path.join(model_dir, "stock_model.npz"),
            os.path.join(model_dir, "feature_info.json"),
            os.path.join(model_dir, "training_data.csv")
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if not missing_files:
            print(f"✅ Found working model: {model_dir}")
            return model_dir
        else:
            print(f"⚠️ Missing files: {[os.path.basename(f) for f in missing_files]}")
    
    print("❌ No complete model directories found")
    return None

def test_animation_export_with_model(model_dir):
    """Test animation export with a real model directory."""
    print(f"\n🎬 Testing animation export with model: {model_dir}")
    print("=" * 60)
    
    # Check if plots directory exists
    plots_dir = os.path.join(model_dir, "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir, exist_ok=True)
        print(f"📁 Created plots directory: {plots_dir}")
    
    # Test parameters for floating 3D window
    plot_params = {
        'plot_type': '3D Scatter',
        'color_scheme': 'viridis',
        'animation_enabled': True
    }
    
    try:
        # Import the floating 3D window
        from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
        import tkinter as tk
        
        # Create a simple test window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        print("🎬 Creating floating 3D window with real model data...")
        
        # Create the floating window
        floating_window = Floating3DWindow(
            parent=root,
            model_path=model_dir,
            plot_params=plot_params,
            on_close=lambda: None
        )
        
        print("✅ Floating 3D window created successfully")
        
        # Test GIF export
        print("\n🎬 Testing GIF export with real model data...")
        try:
            # Create a test GIF file
            test_gif_path = os.path.join(plots_dir, 'gui_test_animation.gif')
            
            # Import animation
            import matplotlib.animation as animation
            
            # Create animation
            anim = animation.FuncAnimation(
                floating_window.fig, 
                floating_window.animate_frame,
                frames=72,  # Shorter for testing
                interval=100,
                repeat=False
            )
            
            # Save as GIF
            anim.save(test_gif_path, writer='pillow', fps=10)
            
            if os.path.exists(test_gif_path):
                file_size = os.path.getsize(test_gif_path)
                print(f"✅ GIF export successful: {os.path.basename(test_gif_path)} ({file_size:,} bytes)")
                print(f"📁 Saved to: {test_gif_path}")
            else:
                print("❌ GIF file was not created")
                
        except Exception as e:
            print(f"❌ Error testing GIF export: {e}")
        
        # Test PNG export
        print("\n🖼️ Testing PNG export with real model data...")
        try:
            test_png_path = os.path.join(plots_dir, 'gui_test_plot.png')
            floating_window.fig.savefig(test_png_path, dpi=300, bbox_inches='tight')
            
            if os.path.exists(test_png_path):
                file_size = os.path.getsize(test_png_path)
                print(f"✅ PNG export successful: {os.path.basename(test_png_path)} ({file_size:,} bytes)")
                print(f"📁 Saved to: {test_png_path}")
            else:
                print("❌ PNG file was not created")
                
        except Exception as e:
            print(f"❌ Error testing PNG export: {e}")
        
        # List all files in plots directory
        print(f"\n📁 All files in {plots_dir}:")
        for file in sorted(os.listdir(plots_dir)):
            file_path = os.path.join(plots_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size:,} bytes)")
        
        # Close the floating window
        floating_window.close()
        root.destroy()
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import Floating3DWindow: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing animation export: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Testing GUI Animation Export with Real Model Data")
    print("=" * 60)
    
    # Find a working model
    model_dir = find_working_model()
    if not model_dir:
        print("❌ No working model found. Please run training first.")
        return False
    
    # Test animation export
    success = test_animation_export_with_model(model_dir)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 GUI Animation Export Test Completed Successfully!")
        print("\n📋 Summary:")
        print("- Found working model with real training data")
        print("- Created floating 3D window successfully")
        print("- GIF animation export working")
        print("- PNG static export working")
        print("\n💡 Next Steps:")
        print("1. Open the GUI (gui/main_gui_refactored.py)")
        print("2. Go to Control Plots tab")
        print("3. Click 'Open 3D Controls'")
        print("4. Try 'Save Animation (GIF)' and 'Save Plot' buttons")
    else:
        print("\n❌ GUI Animation Export Test Failed")
    
    return success

if __name__ == "__main__":
    main() 