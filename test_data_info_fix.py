#!/usr/bin/env python3
"""
Test to verify the data info fix.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_data_info():
    """Test data info handling."""
    try:
        print("Testing data info fix...")
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create data manager
        dm = DataManager()
        
        # Create test data info
        test_info = {
            'file_path': '/test/file.csv',
            'file_size': '1.23 MB',
            'rows': 1000,
            'columns': 5,  # This is an integer, not a list
            'numeric_columns': ['open', 'high', 'low', 'close', 'vol'],
            'categorical_columns': ['ticker'],
            'missing_values': {'open': 0, 'high': 2, 'low': 1},
            'data_types': {},
            'summary_stats': {}
        }
        
        # Test that this doesn't cause an error
        print("✓ Test data info created")
        
        # Test the data panel update method
        from stock_prediction_gui.ui.widgets.data_panel import DataPanel
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        # Create a mock app
        class MockApp:
            def __init__(self):
                self.file_utils = None
        
        app = MockApp()
        
        # Create data panel
        panel = DataPanel(root, app)
        print("✓ Data panel created")
        
        # Test update_data_info
        panel.update_data_info(test_info)
        print("✓ update_data_info completed without error")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Data Info Fix")
    print("=" * 25)
    
    if test_data_info():
        print("\n✅ Fix verified! Data info update should work properly now.")
    else:
        print("\n❌ Fix failed. Please check the error above.")
        sys.exit(1) 