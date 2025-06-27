#!/usr/bin/env python3
"""
Test script to check control panel display and tab visibility.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from main_gui import StockPredictionGUI

def test_control_panel_display():
    """Test that the control panel displays all tabs correctly."""
    print("🧪 Testing control panel display...")
    
    try:
        root = tk.Tk()
        root.title("Control Panel Display Test")
        root.geometry("800x600")
        
        # Create the GUI application
        app = StockPredictionGUI(root)
        
        # Check if control panel exists
        assert hasattr(app, 'control_panel'), "Control panel should exist"
        assert hasattr(app, 'control_notebook'), "Control notebook should exist"
        
        print("✅ Control panel and notebook created")
        
        # Check notebook tabs
        notebook = app.control_notebook
        tabs = notebook.tabs()
        print(f"📋 Found {len(tabs)} tabs in notebook")
        
        expected_tabs = ["Data Selection", "Training Parameters", "Model Management", "Plot Controls", "?"]
        
        for i, tab in enumerate(tabs):
            tab_text = notebook.tab(tab, "text")
            print(f"  Tab {i+1}: '{tab_text}'")
            
            if tab_text in expected_tabs:
                print(f"    ✅ Tab '{tab_text}' found")
            else:
                print(f"    ⚠️ Unexpected tab: '{tab_text}'")
        
        # Check if all expected tabs are present
        actual_tab_texts = [notebook.tab(tab, "text") for tab in tabs]
        missing_tabs = [tab for tab in expected_tabs if tab not in actual_tab_texts]
        
        if missing_tabs:
            print(f"❌ Missing tabs: {missing_tabs}")
            return False
        else:
            print("✅ All expected tabs are present")
        
        # Check notebook configuration
        print(f"📏 Notebook size: {notebook.winfo_width()}x{notebook.winfo_height()}")
        print(f"📏 Frame size: {app.control_panel.frame.winfo_width()}x{app.control_panel.frame.winfo_height()}")
        
        # Check if notebook is visible
        if notebook.winfo_viewable():
            print("✅ Notebook is viewable")
        else:
            print("❌ Notebook is not viewable")
        
        # Check if frame is packed properly
        frame_info = app.control_panel.frame.pack_info()
        print(f"📦 Frame pack info: {frame_info}")
        
        # Force update to see actual sizes
        root.update_idletasks()
        print(f"📏 After update - Notebook size: {notebook.winfo_width()}x{notebook.winfo_height()}")
        print(f"📏 After update - Frame size: {app.control_panel.frame.winfo_width()}x{app.control_panel.frame.winfo_height()}")
        
        # Test tab switching
        print("🔄 Testing tab switching...")
        for i, tab in enumerate(tabs):
            try:
                notebook.select(tab)
                current_tab = notebook.select()
                current_text = notebook.tab(current_tab, "text")
                print(f"  ✅ Switched to tab {i+1}: '{current_text}'")
            except Exception as e:
                print(f"  ❌ Error switching to tab {i+1}: {e}")
        
        print("✅ Control panel display test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in control panel display test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🚀 Starting control panel display test...")
    print()
    
    success = test_control_panel_display()
    
    print()
    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ Control panel display test - PASSED")
        print("\n🎉 The control panel is displaying correctly with all tabs!")
    else:
        print("❌ Control panel display test - FAILED")
        print("\n⚠️ There may be an issue with the control panel display.")

if __name__ == "__main__":
    main() 