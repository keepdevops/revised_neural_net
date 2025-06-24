#!/usr/bin/env python3
"""
Debug script to check 3D axes creation and accessibility.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_3d_axes():
    """Debug 3D axes creation and accessibility."""
    print("🔍 Debugging 3D axes creation...")
    
    # Create root window
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Import and create GUI
        from gui.main_gui import StockPredictionGUI
        app = StockPredictionGUI(root)
        print("✅ GUI created")
        
        # Wait for initialization
        root.update()
        root.after(500)
        root.update()
        
        # Check all attributes of the app
        print("\n🔍 Checking app attributes...")
        app_attrs = [attr for attr in dir(app) if not attr.startswith('_')]
        print(f"App has {len(app_attrs)} attributes")
        
        # Look for 3D-related attributes
        gd_attrs = [attr for attr in app_attrs if 'gd' in attr.lower() or '3d' in attr.lower()]
        print(f"3D-related attributes: {gd_attrs}")
        
        # Check specific attributes
        for attr in gd_attrs:
            try:
                value = getattr(app, attr)
                print(f"  {attr}: {type(value)} = {value}")
            except Exception as e:
                print(f"  {attr}: Error accessing - {e}")
        
        # Check if gd3d_ax exists
        if hasattr(app, 'gd3d_ax'):
            print(f"\n✅ gd3d_ax exists: {type(app.gd3d_ax)}")
            if app.gd3d_ax:
                print(f"  Value: {app.gd3d_ax}")
                print(f"  Has view_init: {hasattr(app.gd3d_ax, 'view_init')}")
            else:
                print("  Value is None/False")
        else:
            print("\n❌ gd3d_ax does not exist")
        
        # Check if gd3d_canvas exists
        if hasattr(app, 'gd3d_canvas'):
            print(f"\n✅ gd3d_canvas exists: {type(app.gd3d_canvas)}")
            if app.gd3d_canvas:
                print(f"  Value: {app.gd3d_canvas}")
            else:
                print("  Value is None/False")
        else:
            print("\n❌ gd3d_canvas does not exist")
        
        # Check control panel attributes
        if hasattr(app, 'control_panel'):
            print(f"\n✅ control_panel exists: {type(app.control_panel)}")
            cp_attrs = [attr for attr in dir(app.control_panel) if not attr.startswith('_')]
            gd_cp_attrs = [attr for attr in cp_attrs if 'gd' in attr.lower() or '3d' in attr.lower()]
            print(f"Control panel 3D attributes: {gd_cp_attrs}")
        else:
            print("\n❌ control_panel does not exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    debug_3d_axes() 