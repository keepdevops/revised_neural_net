#!/usr/bin/env python3
"""
Test script to verify 3D plot animation export functionality (MP4 and GIF).
"""

import os
import sys
import tempfile
import shutil
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_animation_export():
    """Test the animation export functionality."""
    print("🧪 Testing 3D Plot Animation Export Functionality")
    print("=" * 60)
    
    # Create a temporary model directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Created temporary directory: {temp_dir}")
        
        # Create mock training data
        import pandas as pd
        n_points = 100
        data = {
            'feature1': np.random.randn(n_points),
            'feature2': np.random.randn(n_points),
            'feature3': np.random.randn(n_points),
            'target': np.random.randn(n_points)
        }
        training_data = pd.DataFrame(data)
        training_data.to_csv(os.path.join(temp_dir, 'training_data.csv'), index=False)
        
        # Create plots directory
        plots_dir = os.path.join(temp_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        print("📊 Created mock training data")
        
        # Test parameters
        plot_params = {
            'plot_type': '3D Scatter',
            'color_scheme': 'viridis',
            'animation_enabled': True
        }
        
        # Create a simple test window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        try:
            # Import the floating 3D window
            from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
            
            print("🎬 Creating floating 3D window...")
            
            # Create the floating window
            floating_window = Floating3DWindow(
                parent=root,
                model_path=temp_dir,
                plot_params=plot_params,
                on_close=lambda: None
            )
            
            print("✅ Floating 3D window created successfully")
            
            # Test MP4 export
            print("\n🎬 Testing MP4 export...")
            try:
                # Create a test MP4 file
                test_mp4_path = os.path.join(plots_dir, 'test_animation.mp4')
                
                # Create animation
                anim = animation.FuncAnimation(
                    floating_window.fig, 
                    floating_window.animate_frame,
                    frames=36,  # Shorter for testing
                    interval=100,
                    repeat=False
                )
                
                # Try to save as MP4
                try:
                    Writer = animation.writers['ffmpeg']
                    writer = Writer(fps=10, metadata=dict(artist='Test Animation'), bitrate=1800)
                    anim.save(test_mp4_path, writer=writer, dpi=100)
                    
                    if os.path.exists(test_mp4_path):
                        file_size = os.path.getsize(test_mp4_path)
                        print(f"✅ MP4 export successful: {os.path.basename(test_mp4_path)} ({file_size:,} bytes)")
                    else:
                        print("❌ MP4 file was not created")
                        
                except Exception as e:
                    print(f"⚠️ MP4 export failed (expected if ffmpeg not installed): {e}")
                    
            except Exception as e:
                print(f"❌ Error testing MP4 export: {e}")
            
            # Test GIF export
            print("\n🎬 Testing GIF export...")
            try:
                # Create a test GIF file
                test_gif_path = os.path.join(plots_dir, 'test_animation.gif')
                
                # Create animation
                anim = animation.FuncAnimation(
                    floating_window.fig, 
                    floating_window.animate_frame,
                    frames=36,  # Shorter for testing
                    interval=100,
                    repeat=False
                )
                
                # Try to save as GIF
                try:
                    anim.save(test_gif_path, writer='pillow', fps=10)
                    
                    if os.path.exists(test_gif_path):
                        file_size = os.path.getsize(test_gif_path)
                        print(f"✅ GIF export successful: {os.path.basename(test_gif_path)} ({file_size:,} bytes)")
                    else:
                        print("❌ GIF file was not created")
                        
                except Exception as e:
                    print(f"⚠️ GIF export failed: {e}")
                    
            except Exception as e:
                print(f"❌ Error testing GIF export: {e}")
            
            # Test PNG export
            print("\n🖼️ Testing PNG export...")
            try:
                test_png_path = os.path.join(plots_dir, 'test_plot.png')
                floating_window.fig.savefig(test_png_path, dpi=300, bbox_inches='tight')
                
                if os.path.exists(test_png_path):
                    file_size = os.path.getsize(test_png_path)
                    print(f"✅ PNG export successful: {os.path.basename(test_png_path)} ({file_size:,} bytes)")
                else:
                    print("❌ PNG file was not created")
                    
            except Exception as e:
                print(f"❌ Error testing PNG export: {e}")
            
            # List all created files
            print(f"\n📁 Files created in {plots_dir}:")
            for file in os.listdir(plots_dir):
                file_path = os.path.join(plots_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size:,} bytes)")
            
            # Close the floating window
            floating_window.close()
            
        except ImportError as e:
            print(f"❌ Could not import Floating3DWindow: {e}")
            print("Make sure the stock_prediction_gui package is properly installed")
        except Exception as e:
            print(f"❌ Error creating floating window: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up
            root.destroy()
    
    print("\n" + "=" * 60)
    print("🎉 Animation export test completed!")
    print("\n📋 Summary:")
    print("- MP4 export: Requires ffmpeg to be installed")
    print("- GIF export: Requires Pillow (PIL) library")
    print("- PNG export: Should work with standard matplotlib")
    print("\n💡 To install ffmpeg:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu: sudo apt-get install ffmpeg")
    print("  Windows: Download from https://ffmpeg.org/download.html")

if __name__ == "__main__":
    test_animation_export() 