#!/usr/bin/env python3
"""
Quick test to verify the DataManager fix.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_data_manager_fix():
    """Test that the DataManager has the get_data_info method."""
    try:
        print("Testing DataManager fix...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create data manager
        dm = DataManager()
        
        # Test that get_data_info method exists
        if hasattr(dm, 'get_data_info'):
            print("✓ get_data_info method exists")
            
            # Test the method
            data_info = dm.get_data_info()
            print(f"✓ get_data_info returns: {type(data_info)}")
            print(f"  Keys: {list(data_info.keys())}")
            
            return True
        else:
            print("❌ get_data_info method is missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing DataManager: {e}")
        return False

def test_data_loading():
    """Test data loading functionality."""
    try:
        print("\nTesting data loading...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create data manager
        dm = DataManager()
        
        # Test with a sample file
        sample_file = "training_data_sample.csv"
        
        if os.path.exists(sample_file):
            print(f"Testing with: {sample_file}")
            
            # Load data
            success = dm.load_data(sample_file)
            print(f"Load success: {success}")
            
            # Get data info
            data_info = dm.get_data_info()
            print(f"Data info: {data_info.get('rows', 'N/A')} rows, {data_info.get('columns', 'N/A')} columns")
            
            return True
        else:
            print(f"Sample file not found: {sample_file}")
            print("Creating a test CSV file...")
            
            # Create a simple test CSV
            import pandas as pd
            test_data = pd.DataFrame({
                'open': [100, 101, 102],
                'high': [105, 106, 107],
                'low': [95, 96, 97],
                'close': [103, 104, 105],
                'vol': [1000, 1100, 1200]
            })
            test_data.to_csv('test_sample.csv', index=False)
            
            # Test with the created file
            success = dm.load_data('test_sample.csv')
            print(f"Load success: {success}")
            
            data_info = dm.get_data_info()
            print(f"Data info: {data_info.get('rows', 'N/A')} rows, {data_info.get('columns', 'N/A')} columns")
            
            # Clean up
            os.remove('test_sample.csv')
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing data loading: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing DataManager Fix")
    print("=" * 30)
    
    # Test the fix
    if not test_data_manager_fix():
        sys.exit(1)
    
    # Test data loading
    if not test_data_loading():
        sys.exit(1)
    
    print("\n✅ Fix verified! The DataManager now has the get_data_info method.")
    print("You can now run the GUI without the error.") 