#!/usr/bin/env python3
"""
Test script to reproduce and diagnose the prediction completion error.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import sys
import os
import logging

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_prediction_completion_error():
    """Test the prediction completion error handling."""
    print("🧪 Testing Prediction Completion Error Handling")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create test window
    root = tk.Tk()
    root.title("Prediction Completion Error Test")
    root.geometry("800x600")
    
    # Mock app
    class MockApp:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
            self.is_predicting = False
            self.main_window = None
        
        def _on_prediction_completed(self, output_file, error=None):
            """Handle prediction completion."""
            try:
                self.is_predicting = False
                
                if error:
                    if hasattr(self.main_window, 'prediction_failed'):
                        self.main_window.prediction_failed(error)
                    self.logger.error(f"Prediction failed: {error}")
                else:
                    if hasattr(self.main_window, 'prediction_completed'):
                        self.main_window.prediction_completed(output_file)
                    self.logger.info(f"Prediction completed successfully. Results saved to: {output_file}")
                    
            except Exception as e:
                self.logger.error(f"Error handling prediction completion: {e}")
                import traceback
                self.logger.error(f"Prediction completion error traceback: {traceback.format_exc()}")
                
                # Try to provide more context about what failed
                try:
                    if hasattr(self, 'main_window'):
                        self.logger.error(f"Main window exists: {self.main_window is not None}")
                        if hasattr(self.main_window, 'prediction_panel'):
                            self.logger.error(f"Prediction panel exists: {self.main_window.prediction_panel is not None}")
                        else:
                            self.logger.error("Main window has no prediction_panel attribute")
                    else:
                        self.logger.error("App has no main_window attribute")
                except Exception as context_error:
                    self.logger.error(f"Error getting context info: {context_error}")
    
    # Mock main window
    class MockMainWindow:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
            self.prediction_panel = None
        
        def prediction_completed(self, output_file):
            """Handle prediction completion."""
            try:
                self.logger.info(f"Prediction completed: {output_file}")
                # Simulate what might cause an error
                if hasattr(self, 'prediction_panel') and self.prediction_panel:
                    self.logger.info("Prediction panel exists, updating...")
                else:
                    self.logger.warning("No prediction panel available")
            except Exception as e:
                self.logger.error(f"Error in prediction_completed: {e}")
                raise
        
        def prediction_failed(self, error):
            """Handle prediction failure."""
            try:
                self.logger.error(f"Prediction failed: {error}")
            except Exception as e:
                self.logger.error(f"Error in prediction_failed: {e}")
                raise
    
    # Create mock objects
    app = MockApp()
    main_window = MockMainWindow()
    app.main_window = main_window
    
    # Test 1: Normal prediction completion
    print("\n1. Testing normal prediction completion...")
    try:
        app._on_prediction_completed("test_output.csv")
        print("✅ Normal prediction completion successful")
    except Exception as e:
        print(f"❌ Normal prediction completion failed: {e}")
    
    # Test 2: Prediction completion with error
    print("\n2. Testing prediction completion with error...")
    try:
        app._on_prediction_completed(None, "Test error message")
        print("✅ Prediction completion with error successful")
    except Exception as e:
        print(f"❌ Prediction completion with error failed: {e}")
    
    # Test 3: Prediction completion with missing main window
    print("\n3. Testing prediction completion with missing main window...")
    try:
        app.main_window = None
        app._on_prediction_completed("test_output.csv")
        print("✅ Prediction completion with missing main window handled gracefully")
    except Exception as e:
        print(f"❌ Prediction completion with missing main window failed: {e}")
    
    # Test 4: Prediction completion with missing prediction panel
    print("\n4. Testing prediction completion with missing prediction panel...")
    try:
        app.main_window = main_window
        main_window.prediction_panel = None
        app._on_prediction_completed("test_output.csv")
        print("✅ Prediction completion with missing prediction panel handled gracefully")
    except Exception as e:
        print(f"❌ Prediction completion with missing prediction panel failed: {e}")
    
    # Test 5: Prediction completion with exception in main window
    print("\n5. Testing prediction completion with exception in main window...")
    try:
        # Create a main window that raises an exception
        class ExceptionMainWindow:
            def prediction_completed(self, output_file):
                raise Exception("Simulated prediction completion error")
            
            def prediction_failed(self, error):
                raise Exception("Simulated prediction failure error")
        
        app.main_window = ExceptionMainWindow()
        app._on_prediction_completed("test_output.csv")
        print("✅ Prediction completion with exception handled gracefully")
    except Exception as e:
        print(f"❌ Prediction completion with exception failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("The enhanced error handling should now provide detailed information")
    print("about what causes prediction completion errors.")
    print("=" * 60)
    
    # Keep window open for a moment
    root.after(3000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    test_prediction_completion_error() 