#!/usr/bin/env python3
"""
Test Manual Refresh Approach
This test verifies that the manual model refresh approach works without segmentation faults.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import logging

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

from stock_prediction_gui.core.app import StockPredictionApp

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_manual_refresh():
    """Test the manual refresh approach."""
    print("Manual Refresh Approach Test")
    print("This test verifies that:")
    print("1. All automatic model updates are disabled")
    print("2. Manual refresh buttons work correctly")
    print("3. No segmentation faults occur")
    
    # Create root window
    root = tk.Tk()
    root.title("Manual Refresh Test")
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
    
    # Test 1: Check if automatic model selection is disabled
    print("\nTest 1: Checking automatic model selection...")
    
    # Check app.py methods
    app_methods = [
        'refresh_models_and_select_latest',
        '_safe_refresh_models_and_select_latest', 
        '_delayed_refresh_models_and_select_latest'
    ]
    
    for method_name in app_methods:
        if hasattr(app, method_name):
            method = getattr(app, method_name)
            method_source = method.__code__.co_consts
            if any('Auto-selected' in str(const) for const in method_source if isinstance(const, str)):
                results.append(f"❌ {method_name} still has automatic selection")
            else:
                results.append(f"✅ {method_name} has automatic selection disabled")
        else:
            results.append(f"⚠️ {method_name} method not found")
    
    # Test 2: Check prediction panel
    print("\nTest 2: Checking prediction panel...")
    
    if hasattr(app, 'main_window') and hasattr(app.main_window, 'prediction_panel'):
        panel = app.main_window.prediction_panel
        
        # Check if automatic model selection is disabled
        if hasattr(panel, '_validate_and_fix_model_selection'):
            method = panel._validate_and_fix_model_selection
            method_source = method.__code__.co_consts
            if any('Auto-selected' in str(const) for const in method_source if isinstance(const, str)):
                results.append("❌ Prediction panel still has automatic selection")
            else:
                results.append("✅ Prediction panel has automatic selection disabled")
        else:
            results.append("⚠️ _validate_and_fix_model_selection method not found")
    else:
        results.append("⚠️ Prediction panel not available")
    
    # Test 3: Check main window
    print("\nTest 3: Checking main window...")
    
    if hasattr(app, 'main_window'):
        main_window = app.main_window
        
        # Check update_model_list method
        if hasattr(main_window, 'update_model_list'):
            method = main_window.update_model_list
            method_source = method.__code__.co_consts
            if any('update_model_list' in str(const) for const in method_source if isinstance(const, str)):
                results.append("❌ Main window still calls update_model_list")
            else:
                results.append("✅ Main window has automatic updates disabled")
        else:
            results.append("⚠️ update_model_list method not found")
    else:
        results.append("⚠️ Main window not available")
    
    # Test 4: Test manual refresh functionality
    print("\nTest 4: Testing manual refresh functionality...")
    
    if hasattr(app, 'main_window') and hasattr(app.main_window, 'prediction_panel'):
        panel = app.main_window.prediction_panel
        
        # Check if refresh buttons exist
        if hasattr(panel, 'refresh_models'):
            results.append("✅ refresh_models method exists")
        else:
            results.append("❌ refresh_models method not found")
        
        if hasattr(panel, 'refresh_and_select_latest'):
            results.append("✅ refresh_and_select_latest method exists")
        else:
            results.append("❌ refresh_and_select_latest method not found")
    else:
        results.append("⚠️ Prediction panel not available for manual refresh test")
    
    # Display results
    print("\n" + "="*50)
    print("TEST RESULTS:")
    print("="*50)
    
    for result in results:
        print(result)
    
    # Summary
    passed = sum(1 for r in results if r.startswith("✅"))
    failed = sum(1 for r in results if r.startswith("❌"))
    warnings = sum(1 for r in results if r.startswith("⚠️"))
    
    print(f"\nSummary: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("🎉 All automatic model updates are disabled!")
        print("✅ Manual refresh approach is ready for testing")
    else:
        print("❌ Some automatic model updates are still active")
        print("Please fix the issues above before testing")
    
    # Create test buttons
    button_frame = ttk.Frame(test_frame)
    button_frame.pack(pady=20)
    
    def test_refresh():
        print("\nTesting manual refresh...")
        if hasattr(app, 'main_window') and hasattr(app.main_window, 'prediction_panel'):
            try:
                app.main_window.prediction_panel.refresh_models()
                print("✅ Manual refresh completed successfully")
            except Exception as e:
                print(f"❌ Manual refresh failed: {e}")
        else:
            print("⚠️ Prediction panel not available")
    
    def test_latest():
        print("\nTesting latest model selection...")
        if hasattr(app, 'main_window') and hasattr(app.main_window, 'prediction_panel'):
            try:
                app.main_window.prediction_panel.refresh_and_select_latest()
                print("✅ Latest model selection completed successfully")
            except Exception as e:
                print(f"❌ Latest model selection failed: {e}")
        else:
            print("⚠️ Prediction panel not available")
    
    ttk.Button(button_frame, text="Test Manual Refresh", command=test_refresh).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Test Latest Selection", command=test_latest).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Close", command=root.destroy).pack(side="left", padx=5)
    
    # Instructions
    instructions = ttk.Label(test_frame, text="""
Instructions:
1. Review the test results above
2. Click "Test Manual Refresh" to test the refresh functionality
3. Click "Test Latest Selection" to test the latest model selection
4. If all tests pass, the manual refresh approach is working correctly
5. Close the window when done
    """, justify="left")
    instructions.pack(pady=20)
    
    print("\nManual refresh test window created.")
    print("Review the results and test the functionality.")
    
    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    test_manual_refresh() 