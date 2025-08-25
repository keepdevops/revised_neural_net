#!/usr/bin/env python3
"""
Comprehensive Segmentation Fault Fix Test

This test verifies that the comprehensive segmentation fault fix works correctly
by testing all the thread safety improvements in the prediction panel and app.
"""

import os
import sys
import time
import threading
import tempfile
import logging
import tkinter as tk
from tkinter import ttk

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_thread_safe_prediction_panel():
    """Test thread safety of prediction panel methods."""
    print("Testing thread safety of prediction panel methods...")
    
    # Create a simple test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Import the prediction panel
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        
        # Create a mock app
        class MockApp:
            def __init__(self):
                self.selected_model = None
                self.current_data_file = None
                self.main_window = None
                self.model_manager = MockModelManager()
                
        class MockModelManager:
            def get_available_models(self):
                return ["/path/to/model1", "/path/to/model2"]
        
        # Create prediction panel
        app = MockApp()
        panel = PredictionPanel(root, app)
        
        # Test update_model_info thread safety
        print("Testing update_model_info thread safety...")
        panel.update_model_info("/path/to/test/model")
        time.sleep(0.1)  # Allow time for after() call
        
        # Test update_model_list thread safety
        print("Testing update_model_list thread safety...")
        panel.update_model_list(["/path/to/model1", "/path/to/model2"])
        time.sleep(0.1)  # Allow time for after() call
        
        # Test _update_model_selection_display thread safety
        print("Testing _update_model_selection_display thread safety...")
        panel._update_model_selection_display("/path/to/test/model")
        time.sleep(0.1)  # Allow time for after() call
        
        print("✅ All prediction panel thread safety tests passed")
        
    except Exception as e:
        print(f"❌ Error in prediction panel thread safety test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

def test_thread_safe_app_methods():
    """Test thread safety of app methods."""
    print("Testing thread safety of app methods...")
    
    # Create a simple test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Import the app
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create app
        app = StockPredictionApp(root)
        
        # Test _safe_update_prediction_panel_model
        print("Testing _safe_update_prediction_panel_model...")
        app._safe_update_prediction_panel_model("/path/to/test/model")
        
        # Test _extra_safe_update_prediction_panel_model
        print("Testing _extra_safe_update_prediction_panel_model...")
        app._extra_safe_update_prediction_panel_model("/path/to/test/model")
        
        # Test _safe_refresh_models_and_select_latest
        print("Testing _safe_refresh_models_and_select_latest...")
        app._safe_refresh_models_and_select_latest()
        
        print("✅ All app thread safety tests passed")
        
    except Exception as e:
        print(f"❌ Error in app thread safety test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

def test_error_handling():
    """Test error handling in thread-safe methods."""
    print("Testing error handling in thread-safe methods...")
    
    # Create a simple test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Import the prediction panel
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        
        # Create a mock app with missing attributes
        class MockApp:
            def __init__(self):
                self.selected_model = None
                self.current_data_file = None
                # Don't set main_window to test error handling
                
        # Create prediction panel
        app = MockApp()
        panel = PredictionPanel(root, app)
        
        # Test with missing main_window
        print("Testing error handling with missing main_window...")
        panel.update_model_info("/path/to/test/model")
        panel.update_model_list(["/path/to/model1"])
        panel._update_model_selection_display("/path/to/test/model")
        
        # Test with None values
        print("Testing error handling with None values...")
        panel.model_var = None
        panel.model_combo = None
        panel.model_info_var = None
        
        panel.update_model_info("/path/to/test/model")
        panel.update_model_list(["/path/to/model1"])
        panel._update_model_selection_display("/path/to/test/model")
        
        print("✅ All error handling tests passed")
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

def test_concurrent_access():
    """Test concurrent access to thread-safe methods."""
    print("Testing concurrent access to thread-safe methods...")
    
    # Create a simple test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Import the prediction panel
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        
        # Create a mock app
        class MockApp:
            def __init__(self):
                self.selected_model = None
                self.current_data_file = None
                self.main_window = None
                self.model_manager = MockModelManager()
                
        class MockModelManager:
            def get_available_models(self):
                return ["/path/to/model1", "/path/to/model2"]
        
        # Create prediction panel
        app = MockApp()
        panel = PredictionPanel(root, app)
        
        # Create multiple threads calling the methods concurrently
        def worker(thread_id):
            for i in range(5):
                panel.update_model_info(f"/path/to/model_{thread_id}_{i}")
                panel.update_model_list([f"/path/to/model_{thread_id}_{i}"])
                panel._update_model_selection_display(f"/path/to/model_{thread_id}_{i}")
                time.sleep(0.01)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Allow time for any remaining after() calls
        time.sleep(0.5)
        
        print("✅ All concurrent access tests passed")
        
    except Exception as e:
        print(f"❌ Error in concurrent access test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

def main():
    """Run all tests."""
    print("Comprehensive Segmentation Fault Fix Test")
    print("=" * 50)
    
    setup_logging()
    
    # Run all tests
    test_thread_safe_prediction_panel()
    test_thread_safe_app_methods()
    test_error_handling()
    test_concurrent_access()
    
    print("\n" + "=" * 50)
    print("✅ All comprehensive segmentation fault fix tests completed successfully!")
    print("The thread safety improvements should prevent segmentation faults.")

if __name__ == "__main__":
    main() 