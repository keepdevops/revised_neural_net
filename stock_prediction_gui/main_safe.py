#!/usr/bin/env python3
"""
Stock Prediction Neural Network GUI - Safe Version
A clean, modern interface for stock price prediction using neural networks.
"""

import os
import sys
import logging
from datetime import datetime

# Set matplotlib backend before importing matplotlib
import matplotlib
matplotlib.use('TkAgg')

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stock_prediction_gui.log'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Stock Prediction GUI...")
        
        # Import tkinter
        import tkinter as tk
        logger.info("Tkinter imported successfully")
        
        # Import the app
        from stock_prediction_gui.core.app import StockPredictionApp
        logger.info("StockPredictionApp imported successfully")
        
        # Create root window
        logger.info("Creating root window...")
        root = tk.Tk()
        
        # Create and run the application
        logger.info("Creating application...")
        app = StockPredictionApp(root)
        
        logger.info("Starting main loop...")
        root.mainloop()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please check that all required packages are installed.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 