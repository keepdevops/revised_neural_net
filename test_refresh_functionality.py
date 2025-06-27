#!/usr/bin/env python3
"""
Test script to verify the refresh data files functionality.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_refresh_data_files():
    """Test the refresh_data_files functionality."""
    print("🧪 Testing refresh_data_files functionality...")
    
    # Check what CSV files are currently in the directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    print(f"📁 Current CSV files in directory: {csv_files}")
    
    # Test the refresh logic
    try:
        # Simulate the refresh_data_files method logic
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        
        # Simulate history (empty initially)
        data_file_history = []
        
        # Add any new files to history
        for file in csv_files:
            if file not in data_file_history:
                data_file_history.insert(0, file)
        
        print(f"✅ Found {len(csv_files)} CSV files")
        print(f"   Files: {csv_files}")
        print(f"   History: {data_file_history}")
        
        # Check if we have the expected files
        expected_files = ['test_sample_data.csv', 'training_data_sample.csv']
        found_expected = all(f in csv_files for f in expected_files)
        
        print(f"   Expected files present: {'✅ YES' if found_expected else '❌ NO'}")
        
        return len(csv_files) >= 2 and found_expected
        
    except Exception as e:
        print(f"❌ Error testing refresh functionality: {e}")
        return False

def test_gui_refresh_method():
    """Test the actual GUI refresh method."""
    print("\n🧪 Testing GUI refresh method...")
    
    try:
        # Import the GUI class
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
        from main_gui import StockPredictionGUI
        import tkinter as tk
        
        # Create a minimal GUI instance
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create the GUI
        app = StockPredictionGUI(root)
        
        # Test the refresh method
        print("🔄 Calling refresh_data_files()...")
        app.refresh_data_files()
        
        # Check the results
        print(f"   Data file history: {app.data_file_history}")
        print(f"   History length: {len(app.data_file_history)}")
        
        # Check if the expected files are in history
        expected_files = ['test_sample_data.csv', 'training_data_sample.csv']
        found_expected = all(f in app.data_file_history for f in expected_files)
        
        print(f"   Expected files in history: {'✅ YES' if found_expected else '❌ NO'}")
        
        success = len(app.data_file_history) >= 2 and found_expected
        
        root.destroy()
        return success
        
    except Exception as e:
        print(f"❌ Error testing GUI refresh method: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting refresh functionality tests...\n")
    
    # Test 1: Basic refresh logic
    test1_result = test_refresh_data_files()
    
    # Test 2: GUI refresh method
    test2_result = test_gui_refresh_method()
    
    print(f"\n📊 Test Results:")
    print(f"   Basic refresh logic: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   GUI refresh method: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Refresh functionality should work correctly.")
        print("   You can now use the '🔄 Refresh' button in the GUI to update the dropdown list.")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.") 