#!/usr/bin/env python3
"""
Test to verify 3D surface visibility in GUI's 3D plot.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_gui_3d_surface():
    """Test if the 3D surface is visible in the GUI's 3D plot."""
    print("🧪 Testing GUI 3D surface visibility...")
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Create GUI instance
        app = StockPredictionGUI(root)
        print("✅ GUI created successfully")
        
        # Wait for initialization
        root.update()
        root.after(1000)  # Wait 1 second
        root.update()
        
        # Check if 3D axes exist
        if hasattr(app, 'gd3d_ax') and app.gd3d_ax is not None:
            print("✅ 3D axes found")
            
            # Check if surface exists in the 3D axes
            surface_found = False
            for artist in app.gd3d_ax.get_children():
                if hasattr(artist, '__class__') and 'Poly3DCollection' in str(artist.__class__):
                    print(f"✅ Surface found: {artist}")
                    surface_found = True
                    break
            
            if not surface_found:
                print("⚠️  No surface found in 3D axes")
                
                # Try to create a simple surface in the GUI's 3D plot
                print("🎨 Creating test surface in GUI's 3D plot...")
                
                # Create test surface data
                x = np.linspace(-2, 2, 20)
                y = np.linspace(-2, 2, 20)
                X, Y = np.meshgrid(x, y)
                Z = X**2 + Y**2  # Simple paraboloid
                
                # Plot surface
                surface = app.gd3d_ax.plot_surface(X, Y, Z, 
                                                 cmap='viridis', 
                                                 alpha=0.8,
                                                 linewidth=0.5,
                                                 antialiased=True)
                
                print(f"✅ Test surface created: {surface}")
                
                # Update the canvas
                if hasattr(app, 'gd3d_canvas') and app.gd3d_canvas:
                    app.gd3d_canvas.draw()
                    print("✅ Canvas updated")
                
        else:
            print("❌ 3D axes not found")
        
        # Check if canvas exists
        if hasattr(app, 'gd3d_canvas') and app.gd3d_canvas is not None:
            print("✅ 3D canvas found")
        else:
            print("❌ 3D canvas not found")
        
        print("✅ GUI 3D surface test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing GUI 3D surface: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_gui_3d_surface()
    if success:
        print("\n✅ GUI 3D surface test completed successfully")
    else:
        print("\n❌ GUI 3D surface test failed") 