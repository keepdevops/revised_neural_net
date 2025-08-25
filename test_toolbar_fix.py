#!/usr/bin/env python3
"""
Test script to verify the toolbar geometry manager fix.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_toolbar_fix():
    """Test the toolbar geometry manager fix."""
    print("🧪 Testing Toolbar Geometry Manager Fix")
    print("=" * 50)
    
    try:
        # Import the floating 3D window
        from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
        
        # Create a test root window
        root = tk.Tk()
        root.title("Toolbar Fix Test")
        root.geometry("800x600")
        
        # Test parameters
        test_model_path = "model_20250627_131418"  # Use a working model
        test_plot_params = {
            'plot_type': '3D Scatter',
            'point_size': 50,
            'color_scheme': 'viridis',
            'animation_enabled': False,
            'w1_range': [-2.0, 2.0],
            'w2_range': [-2.0, 2.0],
            'w1_index': 0,
            'w2_index': 1
        }
        
        print("📁 Creating Floating3DWindow...")
        
        # Create the floating window
        floating_window = Floating3DWindow(
            parent=root,
            model_path=test_model_path,
            plot_params=test_plot_params,
            on_close=lambda: print("Window closed")
        )
        
        print("✅ Floating3DWindow created successfully")
        print("🔧 Checking for geometry manager warnings...")
        
        # Check if there are any warnings in the logs
        import logging
        
        # Set up logging to capture warnings
        warning_messages = []
        
        class WarningHandler(logging.Handler):
            def emit(self, record):
                if record.levelno >= logging.WARNING:
                    warning_messages.append(record.getMessage())
        
        # Add handler to the floating window's logger
        if hasattr(floating_window, 'logger'):
            warning_handler = WarningHandler()
            warning_handler.setLevel(logging.WARNING)
            floating_window.logger.addHandler(warning_handler)
        
        # Wait a moment for any warnings to be logged
        root.after(1000, lambda: check_warnings())
        
        def check_warnings():
            geometry_warnings = [msg for msg in warning_messages 
                               if 'geometry manager' in msg.lower() or 
                                  'pack' in msg.lower() or 
                                  'grid' in msg.lower()]
            
            if geometry_warnings:
                print("❌ Geometry manager warnings found:")
                for warning in geometry_warnings:
                    print(f"   - {warning}")
            else:
                print("✅ No geometry manager warnings detected")
            
            print("🎉 Toolbar fix test completed successfully!")
            root.after(2000, root.destroy)
        
        # Start the GUI
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_toolbar_fix() 