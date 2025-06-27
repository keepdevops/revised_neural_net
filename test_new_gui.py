#!/usr/bin/env python3
"""
Test script for the new Stock Prediction GUI.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test that all modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test core modules
        from stock_prediction_gui.core.app import StockPredictionApp
        from stock_prediction_gui.core.data_manager import DataManager
        from stock_prediction_gui.core.model_manager import ModelManager
        print("✓ Core modules imported successfully")
        
        # Test UI modules
        from stock_prediction_gui.ui.main_window import MainWindow
        from stock_prediction_gui.ui.widgets.data_panel import DataPanel
        from stock_prediction_gui.ui.widgets.training_panel import TrainingPanel
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        from stock_prediction_gui.ui.widgets.results_panel import ResultsPanel
        print("✓ UI modules imported successfully")
        
        # Test utility modules
        from stock_prediction_gui.utils.file_utils import FileUtils
        from stock_prediction_gui.utils.validation import ValidationUtils
        print("✓ Utility modules imported successfully")
        
        # Test dialog modules
        from stock_prediction_gui.ui.dialogs.settings_dialog import SettingsDialog
        from stock_prediction_gui.ui.dialogs.help_dialog import HelpDialog
        print("✓ Dialog modules imported successfully")
        
        print("\n🎉 All imports successful! The new GUI is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_gui_creation():
    """Test that the GUI can be created."""
    try:
        print("\nTesting GUI creation...")
        
        import tkinter as tk
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
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
    print("🧪 Testing New Stock Prediction GUI")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test GUI creation
    if not test_gui_creation():
        sys.exit(1)
    
    print("\n✅ All tests passed! You can now run the new GUI with:")
    print("   cd stock_prediction_gui")
    print("   python main.py") 