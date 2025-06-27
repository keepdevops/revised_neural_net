#!/usr/bin/env python3
"""
Stock Prediction Neural Network GUI
A clean, modern interface for stock price prediction using neural networks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from stock_prediction_gui.core.app import StockPredictionApp

def main():
    """Main entry point for the application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('stock_prediction_gui.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create and run the application
    root = tk.Tk()
    app = StockPredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 