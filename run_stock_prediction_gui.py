#!/usr/bin/env python3
"""
Stock Prediction GUI Launcher

This script launches the stock prediction GUI from the correct location.
The actual GUI code is in the 'gui' directory, not 'stock_prediction_gui'.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def main():
    """Launch the stock prediction GUI."""
    try:
        # Add the project root to Python path
        project_root = os.path.abspath(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Check if stock_net.py exists
        stock_net_path = os.path.join(project_root, 'stock_net.py')
        if not os.path.exists(stock_net_path):
            messagebox.showerror("Error", f"stock_net.py not found at: {stock_net_path}")
            return
        
        # Check if gui directory exists
        gui_dir = os.path.join(project_root, 'gui')
        if not os.path.exists(gui_dir):
            messagebox.showerror("Error", f"GUI directory not found at: {gui_dir}")
            return
        
        # Check if main_gui.py exists
        main_gui_path = os.path.join(gui_dir, 'main_gui.py')
        if not os.path.exists(main_gui_path):
            messagebox.showerror("Error", f"main_gui.py not found at: {main_gui_path}")
            return
        
        # Import and run the GUI
        print("Launching Stock Prediction GUI...")
        print(f"Project root: {project_root}")
        print(f"GUI path: {main_gui_path}")
        
        # Import the GUI module
        sys.path.insert(0, gui_dir)
        from main_gui import StockPredictionGUI, main
        
        # Run the GUI
        main()
        
    except ImportError as e:
        error_msg = f"Import error: {e}\n\nMake sure all required dependencies are installed."
        print(error_msg)
        messagebox.showerror("Import Error", error_msg)
        
    except Exception as e:
        error_msg = f"Error launching GUI: {e}"
        print(error_msg)
        messagebox.showerror("Launch Error", error_msg)

if __name__ == "__main__":
    main() 