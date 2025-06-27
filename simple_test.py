#!/usr/bin/env python3
"""
Simple test to verify the GUI can start.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test that all required modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test core modules
        from stock_prediction_gui.core.app import StockPredictionApp
        from stock_prediction_gui.core.data_manager import DataManager
        print("✓ Core modules imported")
        
        # Test UI modules
        from stock_prediction_gui.ui.main_window import MainWindow
        print("✓ UI modules imported")
        
        # Test utility modules
        from stock_prediction_gui.utils.file_utils import FileUtils
        print("✓ Utility modules imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_manager():
    """Test the DataManager fix."""
    try:
        print("\nTesting DataManager...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        dm = DataManager()
        
        # Test get_data_info method
        info = dm.get_data_info()
        print(f"✓ get_data_info works: {type(info)}")
        
        return True
        
    except Exception as e:
        print(f"❌ DataManager error: {e}")
        return False

def test_gui_creation():
    """Test GUI creation."""
    try:
        print("\nTesting GUI creation...")
        
        import tkinter as tk
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        
        # Create app
        app = StockPredictionApp(root)
        print("✓ GUI created successfully")
        
        # Clean up
        root.destroy()
        print("✓ GUI cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI creation error: {e}")
        return False

if __name__ == "__main__":
    print("�� Simple GUI Test")
    print("=" * 20)
    
    if test_imports() and test_data_manager() and test_gui_creation():
        print("\n✅ All tests passed! GUI is ready to run.")
        print("\nTo run the GUI, use:")
        print("  python run_gui.py")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1) 