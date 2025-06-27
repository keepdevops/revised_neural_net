#!/usr/bin/env python3
"""
Immediate test to verify the DataManager fix.
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
        
        # Import the DataManager
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create instance
        dm = DataManager()
        print("✓ DataManager created")
        
        # Check if get_data_info method exists
        if hasattr(dm, 'get_data_info'):
            print("✓ get_data_info method exists")
            
            # Test the method
            info = dm.get_data_info()
            print(f"✓ get_data_info returns: {type(info)}")
            print(f"  Keys: {list(info.keys())}")
            
            return True
        else:
            print("❌ get_data_info method is missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_loading():
    """Test data loading."""
    try:
        print("\nTesting data loading...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        dm = DataManager()
        
        # Create a test CSV file
        import pandas as pd
        test_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [103, 104, 105],
            'vol': [1000, 1100, 1200]
        })
        test_file = 'test_data.csv'
        test_data.to_csv(test_file, index=False)
        
        print(f"Created test file: {test_file}")
        
        # Load data
        success = dm.load_data(test_file)
        print(f"Load success: {success}")
        
        # Get data info
        info = dm.get_data_info()
        print(f"Data info: {info['rows']} rows, {info['columns']} columns")
        
        # Clean up
        os.remove(test_file)
        print("✓ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing DataManager Fix")
    print("=" * 30)
    
    if test_data_manager() and test_data_loading():
        print("\n✅ SUCCESS! The fix is working.")
        print("You can now run the GUI without errors.")
    else:
        print("\n❌ FAILED! The fix is not working.")
        sys.exit(1) 