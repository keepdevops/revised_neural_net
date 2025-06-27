#!/usr/bin/env python3
"""
Simple test to launch the GUI
"""

import os
import sys

def main():
    print("Testing GUI launch...")
    
    # Check if gui directory exists
    if not os.path.exists('gui'):
        print("❌ gui directory not found")
        return
    
    # Check for main_gui.py
    gui_file = os.path.join('gui', 'main_gui.py')
    if not os.path.exists(gui_file):
        print(f"❌ {gui_file} not found")
        return
    
    print(f"✅ Found {gui_file}")
    
    # Try to import
    try:
        sys.path.insert(0, 'gui')
        import main_gui
        print("✅ GUI module imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
    
    print("Ready to launch GUI!")

if __name__ == "__main__":
    main() 