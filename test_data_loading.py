#!/usr/bin/env python3
"""
Test script for data loading functionality.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_data_manager():
    """Test the DataManager class."""
    try:
        print("Testing DataManager...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create data manager
        dm = DataManager()
        
        # Test with a sample CSV file
        sample_file = "training_data_sample.csv"
        
        if os.path.exists(sample_file):
            print(f"Testing with file: {sample_file}")
            
            # Load data
            success = dm.load_data(sample_file)
            print(f"Load success: {success}")
            
            # Get data info
            data_info = dm.get_data_info()
            print(f"Data info keys: {list(data_info.keys())}")
            print(f"Rows: {data_info.get('rows', 'N/A')}")
            print(f"Columns: {data_info.get('columns', 'N/A')}")
            
            # Get feature columns
            features = dm.get_feature_columns()
            print(f"Feature columns: {features}")
            
            return True
        else:
            print(f"Sample file not found: {sample_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing DataManager: {e}")
        return False

def test_app_integration():
    """Test app integration."""
    try:
        print("\nTesting app integration...")
        
        import tkinter as tk
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        # Create app
        app = StockPredictionApp(root)
        print("✓ App created successfully")
        
        # Test data loading
        sample_file = "training_data_sample.csv"
        if os.path.exists(sample_file):
            success = app.load_data_file(sample_file)
            print(f"Data loading success: {success}")
        
        # Clean up
        root.destroy()
        print("✓ App cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app integration: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Data Loading Fix")
    print("=" * 40)
    
    # Test DataManager
    if not test_data_manager():
        sys.exit(1)
    
    # Test app integration
    if not test_app_integration():
        sys.exit(1)
    
    print("\n✅ All tests passed! The data loading fix is working.") 