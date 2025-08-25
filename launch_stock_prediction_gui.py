#!/usr/bin/env python3
"""
Stock Prediction GUI Launcher

This script launches the stock_prediction_gui project from the correct directory.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def main():
    """Launch the stock prediction GUI."""
    try:
        # Get the project root directory
        project_root = os.path.abspath(os.path.dirname(__file__))
        
        # Check if stock_prediction_gui directory exists
        gui_dir = os.path.join(project_root, 'stock_prediction_gui')
        if not os.path.exists(gui_dir):
            messagebox.showerror("Error", f"stock_prediction_gui directory not found at: {gui_dir}")
            return
        
        # Check if main.py exists
        main_py = os.path.join(gui_dir, 'main.py')
        if not os.path.exists(main_py):
            messagebox.showerror("Error", f"main.py not found at: {main_py}")
            return
        
        # Check if stock_net.py exists in project root
        stock_net_path = os.path.join(project_root, 'stock_net.py')
        if not os.path.exists(stock_net_path):
            messagebox.showerror("Error", f"stock_net.py not found at: {stock_net_path}")
            return
        
        print("Launching Stock Prediction GUI...")
        print(f"Project root: {project_root}")
        print(f"GUI directory: {gui_dir}")
        print(f"Main script: {main_py}")
        
        # Change to the stock_prediction_gui directory and run main.py
        os.chdir(gui_dir)
        subprocess.run([sys.executable, 'main.py'])
        
    except Exception as e:
        error_msg = f"Error launching GUI: {e}"
        print(error_msg)
        messagebox.showerror("Launch Error", error_msg)

if __name__ == "__main__":
    main() 