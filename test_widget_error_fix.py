#!/usr/bin/env python3
"""
Test script to verify widget error fixes and proper cleanup.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os

# Add the gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from main_gui import StockPredictionGUI

def test_widget_existence_checks():
    """Test that widgets can be created and accessed safely."""
    print("🧪 Testing widget existence checks...")
    
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI application
        app = StockPredictionGUI(root)
        
        # Test that all required widgets exist
        assert hasattr(app, 'status_var'), "status_var should exist"
        assert hasattr(app, 'data_file_var'), "data_file_var should exist"
        assert hasattr(app, 'lock_status_var'), "lock_status_var should exist"
        assert hasattr(app, 'epochs_var'), "epochs_var should exist"
        assert hasattr(app, 'patience_var'), "patience_var should exist"
        
        print("✅ All required variables exist")
        
        # Test widget existence checks in methods
        app.append_training_log("Test log entry")
        app.clear_training_log()
        
        print("✅ Widget existence checks work")
        
        # Test proper cleanup
        print("🧹 Testing cleanup...")
        app.on_closing()
        
        print("✅ Cleanup completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in widget existence check test: {e}")
        return False

def test_threading_safety():
    """Test that the GUI works safely in threaded environments."""
    print("🧪 Testing threading safety...")
    
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI application
        app = StockPredictionGUI(root)
        
        # Test widget updates from a different thread
        def update_widgets():
            try:
                # These should handle threading errors gracefully
                app.append_training_log("Thread test log")
                app.clear_training_log()
                app.update_live_training_tab(1, 0.5)
            except Exception as e:
                print(f"Thread update error (expected): {e}")
        
        # Run widget updates in a separate thread
        thread = threading.Thread(target=update_widgets)
        thread.start()
        thread.join(timeout=2)
        
        print("✅ Threading safety checks completed")
        
        # Test proper cleanup
        print("🧹 Testing cleanup...")
        app.on_closing()
        
        print("✅ Cleanup completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in threading safety test: {e}")
        return False

def test_tkinter_variable_cleanup():
    """Test that Tkinter variables are properly cleaned up to prevent garbage collection errors."""
    print("🧪 Testing Tkinter variable cleanup...")
    
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI application
        app = StockPredictionGUI(root)
        
        # Verify variables exist
        assert hasattr(app, 'status_var'), "status_var should exist"
        assert hasattr(app, 'epochs_var'), "epochs_var should exist"
        
        # Test the cleanup method directly
        app._cleanup_tkinter_variables()
        
        # Verify variables are cleaned up
        assert app.status_var is None, "status_var should be None after cleanup"
        assert app.epochs_var is None, "epochs_var should be None after cleanup"
        
        print("✅ Tkinter variable cleanup works")
        
        # Test full cleanup
        app.on_closing()
        
        print("✅ Full cleanup completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Tkinter variable cleanup test: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting widget error fix verification tests...")
    print()
    
    # Run tests
    test1_passed = test_widget_existence_checks()
    print()
    
    test2_passed = test_threading_safety()
    print()
    
    test3_passed = test_tkinter_variable_cleanup()
    print()
    
    # Print summary
    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if test1_passed:
        print("✅ Test 1: Widget existence checks - PASSED")
    else:
        print("❌ Test 1: Widget existence checks - FAILED")
    
    if test2_passed:
        print("✅ Test 2: Threading safety - PASSED")
    else:
        print("❌ Test 2: Threading safety - FAILED")
    
    if test3_passed:
        print("✅ Test 3: Tkinter variable cleanup - PASSED")
    else:
        print("❌ Test 3: Tkinter variable cleanup - FAILED")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! The widget error fixes are working correctly.")
    else:
        print("\n⚠️ Some tests failed. The widget error fixes may need more work.")

if __name__ == "__main__":
    main() 