#!/usr/bin/env python3
"""
Simple launcher for the Stock Prediction GUI.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Run the GUI directly."""
    try:
        print("🚀 Starting Stock Prediction GUI...")
        
        # Import and run the GUI
        from stock_prediction_gui.main import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available.")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")

if __name__ == "__main__":
    main() 