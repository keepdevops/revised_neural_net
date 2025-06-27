#!/usr/bin/env python3
"""
Test script for recent files error fix
"""

import os
import sys
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_recent_files_fix():
    """Test the recent files error fix."""
    print("🧪 Testing recent files error fix...")
    
    try:
        # Import the components
        from stock_prediction_gui.ui.widgets.data_panel import DataPanel
        from stock_prediction_gui.core.app import StockPredictionApp
        
        print("✅ Successfully imported components")
        
        # Create a test app
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = StockPredictionApp(root)
        
        # Create the data panel
        data_panel = DataPanel(root, app)
        
        print("✅ DataPanel created successfully")
        
        # Test that the update_recent_files method exists
        if hasattr(data_panel, 'update_recent_files'):
            print("✅ update_recent_files method exists")
        else:
            print("❌ update_recent_files method missing")
            return False
        
        # Test calling the method
        try:
            test_files = ["/path/to/file1.csv", "/path/to/file2.csv"]
            data_panel.update_recent_files(test_files)
            print("✅ update_recent_files method works")
        except Exception as e:
            print(f"❌ Error calling update_recent_files: {e}")
            return False
        
        # Test load_recent_files method
        try:
            data_panel.load_recent_files()
            print("✅ load_recent_files method works")
        except Exception as e:
            print(f"❌ Error calling load_recent_files: {e}")
            return False
        
        # Test the main window update_recent_files call
        try:
            from stock_prediction_gui.ui.main_window import MainWindow
            main_window = MainWindow(root, app)
            main_window.update_recent_files(test_files)
            print("✅ MainWindow update_recent_files works")
        except Exception as e:
            print(f"❌ Error in MainWindow update_recent_files: {e}")
            return False
        
        root.destroy()
        
        print("\n✅ All recent files tests passed!")
        print("\n📝 Summary:")
        print("   - DataPanel update_recent_files method: ✅ Added")
        print("   - DataPanel load_recent_files method: ✅ Fixed")
        print("   - MainWindow integration: ✅ Working")
        print("   - Recent files error: ✅ Resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in recent files test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_recent_files_fix()
    if success:
        print("\n🎉 Recent files fix test completed successfully!")
    else:
        print("\n💥 Recent files fix test failed!") 