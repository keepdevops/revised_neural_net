#!/usr/bin/env python3
"""
Launcher script for the new Stock Prediction GUI.
"""

import sys
import os
import subprocess

def main():
    """Launch the new GUI."""
    try:
        # Change to the stock_prediction_gui directory
        gui_dir = os.path.join(os.path.dirname(__file__), 'stock_prediction_gui')
        
        if not os.path.exists(gui_dir):
            print("❌ GUI directory not found. Please make sure stock_prediction_gui/ exists.")
            return
        
        # Change to the GUI directory
        os.chdir(gui_dir)
        
        # Run the GUI
        print("🚀 Launching new Stock Prediction GUI...")
        subprocess.run([sys.executable, 'main.py'])
        
    except KeyboardInterrupt:
        print("\n GUI closed by user.")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

if __name__ == "__main__":
    main() 