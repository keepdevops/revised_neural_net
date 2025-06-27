#!/usr/bin/env python3
"""
Simple test to run the GUI and check control panel display.
"""

import tkinter as tk
import sys
import os

# Add the gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

def run_gui_test():
    """Run the GUI and provide instructions for testing."""
    print("🚀 Starting GUI display test...")
    print("📋 Instructions:")
    print("1. Look at the left panel in the main window")
    print("2. You should see tabs at the top: 'Data Selection', 'Training Parameters', 'Model Management', 'Plot Controls', '?'")
    print("3. Click on each tab to verify they work")
    print("4. Close the window when done testing")
    print()
    
    try:
        from main_gui import StockPredictionGUI
        
        # Create root window
        root = tk.Tk()
        
        # Create GUI
        app = StockPredictionGUI(root)
        
        # Add a test label to make it clear this is a test
        test_label = tk.Label(root, text="GUI DISPLAY TEST - Check the left panel tabs!", 
                             font=("Arial", 12, "bold"), fg="red", bg="yellow")
        test_label.pack(side=tk.TOP, pady=5)
        
        print("✅ GUI created successfully")
        print("🔍 Please check the left panel tabs now...")
        
        # Run the GUI
        root.mainloop()
        
        print("✅ GUI test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error running GUI test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_gui_test() 