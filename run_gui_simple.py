#!/usr/bin/env python3
"""
Simple launcher for the Stock Prediction GUI.
"""

import sys
import os
import traceback

def main():
    """Launch the GUI with error handling."""
    try:
        print("🚀 Starting Stock Prediction GUI...")
        
        # Change to the stock_prediction_gui directory
        gui_dir = os.path.join(os.path.dirname(__file__), 'stock_prediction_gui')
        
        if not os.path.exists(gui_dir):
            print(f"❌ GUI directory not found: {gui_dir}")
            return
        
        # Change to the GUI directory
        os.chdir(gui_dir)
        print(f"✓ Changed to directory: {os.getcwd()}")
        
        # Add the project root to the Python path
        project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        print(f"✓ Added to Python path: {project_root}")
        
        # Import and run the GUI
        from stock_prediction_gui.main import main as gui_main
        gui_main()
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Please check that all required files exist.")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all required modules are available.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Full error details:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 