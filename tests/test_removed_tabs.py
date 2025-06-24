#!/usr/bin/env python3
"""
Test script to verify that Live Training and 3D Gradient Descent tabs 
have been successfully removed from the Results Panel.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_removed_tabs():
    """Test that the Live Training and 3D Gradient Descent tabs have been removed."""
    print("Testing removal of Live Training and 3D Gradient Descent tabs from Results Panel")
    print("=" * 70)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create GUI instance
        app = StockPredictionGUI(root)
        
        # Get the display notebook tabs
        display_notebook = app.display_notebook
        tabs = []
        
        # Get all tab names
        for i in range(display_notebook.index('end')):
            tab_name = display_notebook.tab(i, "text")
            tabs.append(tab_name)
        
        print(f"Found {len(tabs)} tabs in Results Panel:")
        for i, tab in enumerate(tabs):
            print(f"  {i+1}. {tab}")
        
        # Check that the removed tabs are not present
        removed_tabs = ["Live Training", "3D Gradient Descent"]
        found_removed_tabs = []
        
        for tab in removed_tabs:
            if tab in tabs:
                found_removed_tabs.append(tab)
        
        if found_removed_tabs:
            print(f"\n❌ FAILED: Found removed tabs that should not be present:")
            for tab in found_removed_tabs:
                print(f"   - {tab}")
            return False
        else:
            print(f"\n✅ SUCCESS: All removed tabs are absent from Results Panel")
            print(f"   - 'Live Training' tab: Not found ✓")
            print(f"   - '3D Gradient Descent' tab: Not found ✓")
        
        # Check that expected tabs are still present
        expected_tabs = ["Training Results", "Prediction Results", "Plots", "Saved Plots", "Live Training Plot"]
        missing_tabs = []
        
        for tab in expected_tabs:
            if tab not in tabs:
                missing_tabs.append(tab)
        
        if missing_tabs:
            print(f"\n❌ FAILED: Missing expected tabs:")
            for tab in missing_tabs:
                print(f"   - {tab}")
            return False
        else:
            print(f"\n✅ SUCCESS: All expected tabs are present")
            for tab in expected_tabs:
                print(f"   - {tab}: Found ✓")
        
        # Test that the GUI can still be closed properly
        root.destroy()
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"The Live Training and 3D Gradient Descent tabs have been successfully")
        print(f"removed from the Results Panel while preserving all other functionality.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_removed_tabs()
    sys.exit(0 if success else 1) 