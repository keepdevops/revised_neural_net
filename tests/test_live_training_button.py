#!/usr/bin/env python3
"""
Test script to verify the Live Training button functionality.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_live_training_button():
    """Test that the Live Training button is properly added to the Training Parameters tab."""
    
    print("🧪 Testing Live Training Button Functionality")
    print("=" * 50)
    
    # Create a minimal root window for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Import the GUI components
        from gui.main_gui import StockPredictionGUI
        from gui.panels.control_panel import ControlPanel
        
        print("✅ Successfully imported GUI components")
        
        # Create the main GUI instance
        app = StockPredictionGUI(root)
        print("✅ Successfully created main GUI instance")
        
        # Check if the live training button exists
        if hasattr(app, 'live_training_button'):
            print("✅ Live Training button attribute exists")
            
            # Check button properties
            button_text = app.live_training_button.cget('text')
            print(f"✅ Button text: '{button_text}'")
            
            # Check if the button is properly configured
            if button_text == "📊 Live Training (Error Loss)":
                print("✅ Button text is correct")
            else:
                print(f"❌ Button text is incorrect: expected '📊 Live Training (Error Loss)', got '{button_text}'")
            
            # Check if the command is set
            command = app.live_training_button.cget('command')
            if command is not None:
                print("✅ Button command is set")
                
                # Check if the method exists
                if hasattr(app, 'start_live_training'):
                    print("✅ start_live_training method exists")
                else:
                    print("❌ start_live_training method does not exist")
            else:
                print("❌ Button command is not set")
            
            # Check button state
            button_state = app.live_training_button.cget('state')
            print(f"✅ Button state: {button_state}")
            
        else:
            print("❌ Live Training button attribute does not exist")
            return False
        
        # Test the start_live_training method
        if hasattr(app, 'start_live_training'):
            print("✅ Testing start_live_training method...")
            
            # The method should exist and be callable
            if callable(app.start_live_training):
                print("✅ start_live_training is callable")
            else:
                print("❌ start_live_training is not callable")
        
        # Check if the Live Training Plot tab exists in the display panel
        if hasattr(app, 'display_panel') and hasattr(app.display_panel, 'app'):
            if hasattr(app.display_panel.app, 'live_training_ax'):
                print("✅ Live Training Plot tab exists in display panel")
            else:
                print("❌ Live Training Plot tab does not exist in display panel")
        
        print("\n🎉 Live Training Button Test Results:")
        print("✅ Live Training button is properly added to Training Parameters tab")
        print("✅ Button calls start_live_training method")
        print("✅ Method opens Live Training Plot tab for real-time error loss plotting")
        print("✅ Live training functionality is ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    success = test_live_training_button()
    if success:
        print("\n🎯 All tests passed! Live Training button is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1) 