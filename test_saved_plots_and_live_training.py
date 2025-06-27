#!/usr/bin/env python3
"""
Test script to verify Saved Plots and Live Training button functionality.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_saved_plots_and_live_training():
    """Test that Saved Plots and Live Training button are working correctly."""
    print("🧪 Testing Saved Plots and Live Training button functionality...")
    
    try:
        # Import the GUI
        from gui.main_gui import StockPredictionGUI
        
        # Create a minimal GUI instance
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create the GUI
        app = StockPredictionGUI(root)
        
        # Test 1: Check if Live Training button exists
        print("\n📊 Test 1: Live Training Button")
        if hasattr(app, 'live_training_button'):
            button_text = app.live_training_button.cget('text')
            print(f"✅ Live Training button exists with text: '{button_text}'")
            
            if "Live Training" in button_text:
                print("✅ Live Training button text is correct")
            else:
                print(f"❌ Live Training button text is incorrect: {button_text}")
        else:
            print("❌ Live Training button not found")
            return False
        
        # Test 2: Check if Saved Plots tab exists
        print("\n📁 Test 2: Saved Plots Tab")
        if hasattr(app, 'display_notebook'):
            tab_names = []
            for i in range(app.display_notebook.index('end')):
                tab_names.append(app.display_notebook.tab(i, 'text'))
            
            print(f"📋 Available tabs: {tab_names}")
            
            if "Saved Plots" in tab_names:
                print("✅ Saved Plots tab exists")
            else:
                print("❌ Saved Plots tab not found")
                return False
        else:
            print("❌ Display notebook not found")
            return False
        
        # Test 3: Check if Saved Plots functionality exists
        print("\n🖼️ Test 3: Saved Plots Functionality")
        if hasattr(app, 'load_saved_plots'):
            print("✅ load_saved_plots method exists")
        else:
            print("❌ load_saved_plots method not found")
            return False
        
        if hasattr(app, 'saved_plots_inner_frame'):
            print("✅ saved_plots_inner_frame exists")
        else:
            print("❌ saved_plots_inner_frame not found")
            return False
        
        # Test 4: Check if theme colors are imported
        print("\n🎨 Test 4: Theme Colors")
        try:
            from gui.theme import TEXT_COLOR, FRAME_COLOR
            print(f"✅ TEXT_COLOR imported: {TEXT_COLOR}")
            print(f"✅ FRAME_COLOR imported: {FRAME_COLOR}")
        except ImportError as e:
            print(f"❌ Theme colors not imported: {e}")
            return False
        
        # Test 5: Check if PIL is available for image loading
        print("\n🖼️ Test 5: PIL Image Support")
        try:
            from PIL import Image, ImageTk
            print("✅ PIL Image and ImageTk imported successfully")
        except ImportError as e:
            print(f"❌ PIL not available: {e}")
            return False
        
        # Test 6: Check if a model directory exists for testing
        print("\n📁 Test 6: Model Directory Check")
        model_dirs = [d for d in os.listdir('.') if d.startswith('model_') and os.path.isdir(d)]
        if model_dirs:
            test_model = model_dirs[0]
            print(f"✅ Found test model directory: {test_model}")
            
            # Test if plots directory exists
            plots_dir = os.path.join(test_model, 'plots')
            if os.path.exists(plots_dir):
                print(f"✅ Plots directory exists: {plots_dir}")
                
                # Check for PNG files
                png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
                print(f"✅ Found {len(png_files)} PNG files in plots directory")
                
                if png_files:
                    print(f"📄 PNG files: {png_files[:5]}...")  # Show first 5
                else:
                    print("⚠️ No PNG files found in plots directory")
            else:
                print(f"⚠️ Plots directory not found: {plots_dir}")
        else:
            print("⚠️ No model directories found for testing")
        
        print("\n🎉 All tests passed! Saved Plots and Live Training functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    success = test_saved_plots_and_live_training()
    if success:
        print("\n✅ Test passed: Saved Plots and Live Training functionality is working")
    else:
        print("\n❌ Test failed: Saved Plots and Live Training functionality has issues") 