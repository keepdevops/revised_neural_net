#!/usr/bin/env python3
"""
Test script to verify the MPEG button in the Model Management tab
and check for any duplicates.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_mpeg_button():
    """Test that the MPEG button exists in the Model Management tab and check for duplicates."""
    print("Testing MPEG button in Model Management tab")
    print("=" * 50)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create GUI
        app = StockPredictionGUI(root)
        
        # Get the control notebook
        control_notebook = app.control_notebook
        
        # Find the Model Management tab
        model_management_tab = None
        for i in range(control_notebook.index('end')):
            tab_text = control_notebook.tab(i, 'text')
            if tab_text == "Model Management":
                model_management_tab = control_notebook.winfo_children()[i]
                break
        
        if model_management_tab is None:
            print("❌ Model Management tab not found")
            return False
        
        print("✅ Model Management tab found")
        
        # Count MPEG generation buttons
        mpeg_buttons = []
        for widget in model_management_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        if "MPEG" in child.cget('text') or "🎬" in child.cget('text'):
                            mpeg_buttons.append(child)
                            print(f"Found MPEG button: {child.cget('text')}")
        
        print(f"Total MPEG buttons found: {len(mpeg_buttons)}")
        
        if len(mpeg_buttons) == 1:
            print("✅ Correct: Only one MPEG button found")
            return True
        elif len(mpeg_buttons) == 0:
            print("❌ Error: No MPEG button found")
            return False
        else:
            print(f"❌ Error: {len(mpeg_buttons)} MPEG buttons found (duplicates)")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    success = test_mpeg_button()
    if success:
        print("\n✅ Test passed: MPEG button configuration is correct")
    else:
        print("\n❌ Test failed: MPEG button configuration has issues")
    sys.exit(0 if success else 1) 