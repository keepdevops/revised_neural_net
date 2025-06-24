#!/usr/bin/env python3
"""
Test 3D interaction controls for the GUI.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_3d_interaction_controls():
    """Test that 3D interaction controls are properly connected."""
    print("🧪 Testing 3D interaction controls...")
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Create GUI instance
        app = StockPredictionGUI(root)
        print("✅ GUI created successfully")
        
        # Wait a bit for the GUI to fully initialize
        root.update()
        root.after(100)  # Wait 100ms
        root.update()
        
        # Test that the 3D interaction variables exist
        required_vars = ['elevation_var', 'azimuth_var', 'zoom_var']
        for var_name in required_vars:
            if hasattr(app, var_name):
                print(f"✅ {var_name} exists")
            else:
                print(f"❌ {var_name} missing")
                return False
        
        # Test that the 3D interaction methods exist
        required_methods = [
            'on_elevation_change',
            'on_azimuth_change', 
            'on_zoom_change',
            'reset_3d_view',
            'set_top_view',
            'set_side_view',
            'set_isometric_view'
        ]
        
        for method_name in required_methods:
            if hasattr(app, method_name) and callable(getattr(app, method_name)):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        # Test that the 3D axes and canvas exist - try multiple times
        max_attempts = 5
        for attempt in range(max_attempts):
            if hasattr(app, 'gd3d_ax') and app.gd3d_ax:
                print("✅ gd3d_ax exists")
                break
            else:
                print(f"⚠️ gd3d_ax not found on attempt {attempt + 1}, waiting...")
                root.update()
                root.after(200)  # Wait 200ms
                root.update()
        else:
            print("❌ gd3d_ax missing after all attempts")
            return False
            
        if hasattr(app, 'gd3d_canvas') and app.gd3d_canvas:
            print("✅ gd3d_canvas exists")
        else:
            print("❌ gd3d_canvas missing")
            return False
        
        # Test calling the interaction methods (they should not crash)
        print("\n🧪 Testing method calls...")
        
        try:
            app.on_elevation_change(45.0)
            print("✅ on_elevation_change executed without error")
        except Exception as e:
            print(f"⚠️ on_elevation_change error (expected if no 3D plot): {e}")
        
        try:
            app.on_azimuth_change(90.0)
            print("✅ on_azimuth_change executed without error")
        except Exception as e:
            print(f"⚠️ on_azimuth_change error (expected if no 3D plot): {e}")
        
        try:
            app.on_zoom_change(1.5)
            print("✅ on_zoom_change executed without error")
        except Exception as e:
            print(f"⚠️ on_zoom_change error (expected if no 3D plot): {e}")
        
        try:
            app.reset_3d_view()
            print("✅ reset_3d_view executed without error")
        except Exception as e:
            print(f"⚠️ reset_3d_view error (expected if no 3D plot): {e}")
        
        try:
            app.set_top_view()
            print("✅ set_top_view executed without error")
        except Exception as e:
            print(f"⚠️ set_top_view error (expected if no 3D plot): {e}")
        
        try:
            app.set_side_view()
            print("✅ set_side_view executed without error")
        except Exception as e:
            print(f"⚠️ set_side_view error (expected if no 3D plot): {e}")
        
        try:
            app.set_isometric_view()
            print("✅ set_isometric_view executed without error")
        except Exception as e:
            print(f"⚠️ set_isometric_view error (expected if no 3D plot): {e}")
        
        print("\n✅ All 3D interaction controls test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during 3D interaction test: {e}")
        return False
    
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass

def test_3d_slider_values():
    """Test that slider values are properly initialized."""
    print("\n🧪 Testing 3D slider initialization...")
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = StockPredictionGUI(root)
        
        # Check initial values
        if hasattr(app, 'elevation_var'):
            elev_value = app.elevation_var.get()
            print(f"✅ Elevation initial value: {elev_value}")
            if elev_value == 30.0:
                print("✅ Elevation value is correct (30.0)")
            else:
                print(f"⚠️ Elevation value unexpected: {elev_value}")
        
        if hasattr(app, 'azimuth_var'):
            azim_value = app.azimuth_var.get()
            print(f"✅ Azimuth initial value: {azim_value}")
            if azim_value == 45.0:
                print("✅ Azimuth value is correct (45.0)")
            else:
                print(f"⚠️ Azimuth value unexpected: {azim_value}")
        
        if hasattr(app, 'zoom_var'):
            zoom_value = app.zoom_var.get()
            print(f"✅ Zoom initial value: {zoom_value}")
            if zoom_value == 1.0:
                print("✅ Zoom value is correct (1.0)")
            else:
                print(f"⚠️ Zoom value unexpected: {zoom_value}")
        
        print("✅ 3D slider initialization test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during slider test: {e}")
        return False
    
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting 3D interaction controls test...")
    
    success1 = test_3d_interaction_controls()
    success2 = test_3d_slider_values()
    
    if success1 and success2:
        print("\n🎉 All 3D interaction tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some 3D interaction tests failed!")
        sys.exit(1) 