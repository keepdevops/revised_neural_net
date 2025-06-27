#!/usr/bin/env python3
"""
Final test for recent files fix
"""

import os
import sys
import tempfile
import tkinter as tk

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_recent_files_final_fix():
    """Test the final recent files fix."""
    print("🧪 Testing final recent files fix...")
    
    try:
        from stock_prediction_gui.ui.widgets.data_panel import DataPanel
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create the app
        app = StockPredictionApp(root)
        
        # Create the data panel
        data_panel = DataPanel(root, app)
        
        print("✅ Successfully created DataPanel and App")
        
        # Test 1: Check if update_recent_files method exists
        if hasattr(data_panel, 'update_recent_files'):
            print("✅ update_recent_files method exists")
        else:
            print("❌ update_recent_files method missing")
            return False
        
        # Test 2: Test calling update_recent_files without parameters
        try:
            data_panel.update_recent_files()
            print("✅ update_recent_files() without parameters works")
        except Exception as e:
            print(f"❌ Error calling update_recent_files() without parameters: {e}")
            return False
        
        # Test 3: Test calling update_recent_files with parameters
        test_files = ["/path/to/test1.csv", "/path/to/test2.csv"]
        try:
            data_panel.update_recent_files(test_files)
            print("✅ update_recent_files() with parameters works")
        except Exception as e:
            print(f"❌ Error calling update_recent_files() with parameters: {e}")
            return False
        
        # Test 4: Test the app's load_recent_files method
        try:
            app.load_recent_files()
            print("✅ App load_recent_files() works")
        except Exception as e:
            print(f"❌ Error in app load_recent_files(): {e}")
            return False
        
        # Test 5: Test the main window update_recent_files call
        try:
            app.main_window.update_recent_files(test_files)
            print("✅ MainWindow update_recent_files works")
        except Exception as e:
            print(f"❌ Error in MainWindow update_recent_files: {e}")
            return False
        
        # Clean up
        root.destroy()
        
        print("\n✅ All recent files tests passed!")
        print("\n📝 Summary:")
        print("   - DataPanel update_recent_files method: ✅ Working")
        print("   - Method accepts optional parameters: ✅ Working")
        print("   - App load_recent_files: ✅ Working")
        print("   - MainWindow update_recent_files: ✅ Working")
        print("   - No more 'update_recent_files' errors: ✅ Fixed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in recent files final test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_recent_files_final_fix()
    if success:
        print("\n🎉 Recent files final fix test completed!")
    else:
        print("\n💥 Recent files final fix test failed!") 