#!/usr/bin/env python3
"""
Test Segmentation Fault Isolation
This test helps isolate where the segmentation fault is occurring after training completion.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import logging
import threading
import time

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

from stock_prediction_gui.core.app import StockPredictionApp

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_training_completion_isolation():
    """Test to isolate the segmentation fault after training completion."""
    print("Segmentation Fault Isolation Test")
    print("This test helps identify where the segmentation fault occurs after training completion.")
    
    # Create root window
    root = tk.Tk()
    root.title("Segmentation Fault Isolation Test")
    root.geometry("800x600")
    
    # Setup logging
    setup_logging()
    
    # Create app
    app = StockPredictionApp(root)
    
    # Create test frame
    test_frame = ttk.Frame(root, padding="10")
    test_frame.pack(fill="both", expand=True)
    
    # Test results
    results = []
    
    def simulate_training_completion():
        """Simulate training completion to test for segmentation faults."""
        print("\nSimulating training completion...")
        
        # Test 1: Basic training completion
        print("Test 1: Basic training completion...")
        try:
            model_dir = "/Users/porupine/Desktop/revised_neural_net/test_model"
            app._on_training_completed(model_dir)
            results.append("✅ Basic training completion passed")
        except Exception as e:
            results.append(f"❌ Basic training completion failed: {e}")
        
        # Test 2: GUI handler
        print("Test 2: GUI handler...")
        try:
            model_dir = "/Users/porupine/Desktop/revised_neural_net/test_model"
            app._handle_training_completion_gui(model_dir)
            results.append("✅ GUI handler passed")
        except Exception as e:
            results.append(f"❌ GUI handler failed: {e}")
        
        # Test 3: Main window training completed
        print("Test 3: Main window training completed...")
        try:
            if hasattr(app, 'main_window'):
                model_dir = "/Users/porupine/Desktop/revised_neural_net/test_model"
                app.main_window.training_completed(model_dir)
                results.append("✅ Main window training completed passed")
            else:
                results.append("⚠️ Main window not available")
        except Exception as e:
            results.append(f"❌ Main window training completed failed: {e}")
        
        # Test 4: Model manager operations
        print("Test 4: Model manager operations...")
        try:
            if hasattr(app, 'model_manager'):
                models = app.model_manager.get_available_models()
                results.append(f"✅ Model manager operations passed ({len(models)} models)")
            else:
                results.append("⚠️ Model manager not available")
        except Exception as e:
            results.append(f"❌ Model manager operations failed: {e}")
        
        # Test 5: Prediction panel operations
        print("Test 5: Prediction panel operations...")
        try:
            if hasattr(app, 'main_window') and hasattr(app.main_window, 'prediction_panel'):
                panel = app.main_window.prediction_panel
                # Test basic operations
                if hasattr(panel, 'refresh_models'):
                    results.append("✅ Prediction panel operations passed")
                else:
                    results.append("⚠️ Prediction panel refresh_models not available")
            else:
                results.append("⚠️ Prediction panel not available")
        except Exception as e:
            results.append(f"❌ Prediction panel operations failed: {e}")
        
        # Test 6: Force GUI repaint
        print("Test 6: Force GUI repaint...")
        try:
            if hasattr(app, 'main_window'):
                app.main_window.force_complete_repaint()
                results.append("✅ Force GUI repaint passed")
            else:
                results.append("⚠️ Main window not available")
        except Exception as e:
            results.append(f"❌ Force GUI repaint failed: {e}")
        
        # Display results
        print("\n" + "="*50)
        print("ISOLATION TEST RESULTS:")
        print("="*50)
        
        for result in results:
            print(result)
        
        # Summary
        passed = sum(1 for r in results if r.startswith("✅"))
        failed = sum(1 for r in results if r.startswith("❌"))
        warnings = sum(1 for r in results if r.startswith("⚠️"))
        
        print(f"\nSummary: {passed} passed, {failed} failed, {warnings} warnings")
        
        if failed == 0:
            print("🎉 All isolation tests passed!")
            print("The segmentation fault might be in a different component.")
        else:
            print("❌ Some isolation tests failed")
            print("This helps identify where the segmentation fault occurs.")
    
    # Create test buttons
    button_frame = ttk.Frame(test_frame)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="Run Isolation Tests", command=simulate_training_completion).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Close", command=root.destroy).pack(side="left", padx=5)
    
    # Instructions
    instructions = ttk.Label(test_frame, text="""
Segmentation Fault Isolation Test Instructions:

1. Click "Run Isolation Tests" to test each component individually
2. Review the results to identify which component causes the segmentation fault
3. The test simulates training completion without actual training
4. This helps isolate where the crash occurs
5. Close the window when done

Note: This test helps identify the root cause of the segmentation fault.
    """, justify="left")
    instructions.pack(pady=20)
    
    print("\nSegmentation fault isolation test window created.")
    print("Click 'Run Isolation Tests' to identify the problematic component.")
    
    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    test_training_completion_isolation() 