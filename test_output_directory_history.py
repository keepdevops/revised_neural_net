#!/usr/bin/env python3
"""
Test script for output directory history functionality.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_output_directory_history():
    """Test the output directory history functionality."""
    print("Testing Output Directory History Functionality")
    print("=" * 50)
    
    try:
        # Import the required modules
        from stock_prediction_gui.utils.file_utils import FileUtils
        
        # Create a FileUtils instance
        file_utils = FileUtils()
        
        # Test adding output directories
        test_dirs = [
            "/Users/test/dir1",
            "/Users/test/dir2", 
            "/Users/test/dir3",
            "/Users/test/dir4"
        ]
        
        print("Adding test directories to history...")
        for directory in test_dirs:
            file_utils.add_output_dir(directory)
            print(f"  Added: {directory}")
        
        # Test getting recent output directories
        print("\nRetrieving recent output directories...")
        recent_dirs = file_utils.get_recent_output_dirs()
        print(f"  Found {len(recent_dirs)} directories:")
        for i, directory in enumerate(recent_dirs, 1):
            print(f"    {i}. {directory}")
        
        # Test the history file
        print(f"\nHistory file location: {os.path.abspath(file_utils.history_file)}")
        if os.path.exists(file_utils.history_file):
            print("  History file exists ✓")
            with open(file_utils.history_file, 'r') as f:
                import json
                history = json.load(f)
                print(f"  Output directories in history: {len(history.get('output_dirs', []))}")
        else:
            print("  History file does not exist ✗")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False

def test_gui_integration():
    """Test the GUI integration with output directory history."""
    print("\nTesting GUI Integration")
    print("=" * 30)
    
    try:
        # Create a simple test window
        root = tk.Tk()
        root.title("Output Directory History Test")
        root.geometry("600x400")
        
        # Import the data panel
        from stock_prediction_gui.ui.widgets.data_panel import DataPanel
        
        # Create a mock app object
        class MockApp:
            def __init__(self):
                from stock_prediction_gui.utils.file_utils import FileUtils
                self.file_utils = FileUtils()
                self.current_output_dir = None
                self.current_data_file = None
                
                # Mock data manager
                class MockDataManager:
                    def get_supported_formats_info(self):
                        return {'formats': {'CSV': ['.csv'], 'JSON': ['.json']}}
                    def load_data(self, file_path):
                        return {'file_path': file_path, 'rows': 100, 'columns': 5}
                    def get_current_data(self):
                        return None
                
                self.data_manager = MockDataManager()
                
                # Mock methods
                def set_selected_features(features):
                    pass
                def set_selected_target(target):
                    pass
                
                self.set_selected_features = set_selected_features
                self.set_selected_target = set_selected_target
        
        app = MockApp()
        
        # Create the data panel
        data_panel = DataPanel(root, app)
        data_panel.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add some test directories
        test_dirs = [
            "/Users/test/output1",
            "/Users/test/output2",
            "/Users/test/output3"
        ]
        
        for directory in test_dirs:
            app.file_utils.add_output_dir(directory)
        
        print("GUI test window created successfully!")
        print("Check the 'Output Directory' dropdown - it should show the test directories")
        print("Close the window to continue...")
        
        root.mainloop()
        
        print("GUI test completed!")
        return True
        
    except Exception as e:
        print(f"Error during GUI test: {e}")
        return False

def main():
    """Main test function."""
    print("Output Directory History Test Suite")
    print("=" * 40)
    
    # Test 1: File utilities
    success1 = test_output_directory_history()
    
    # Test 2: GUI integration
    success2 = test_gui_integration()
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    print(f"File Utilities Test: {'✓ PASSED' if success1 else '✗ FAILED'}")
    print(f"GUI Integration Test: {'✓ PASSED' if success2 else '✗ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Output directory history should be working correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main() 