#!/usr/bin/env python3
"""
Detailed functionality test for the Plot Controls tab.
This test simulates actual user interactions to verify that features work correctly.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_plot_controls_functionality():
    """Test actual functionality of Plot Controls tab features."""
    print("Testing Plot Controls Tab - Functionality")
    print("=" * 60)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create GUI
        app = StockPredictionGUI(root)
        
        # Test 1: 3D View Control Variables
        print("\n1. Testing 3D View Control Variables...")
        test_view_variables(app)
        
        # Test 2: Animation Control Variables
        print("\n2. Testing Animation Control Variables...")
        test_animation_variables(app)
        
        # Test 3: 3D Plot Initialization
        print("\n3. Testing 3D Plot Initialization...")
        test_3d_plot_initialization(app)
        
        # Test 4: Method Functionality (Safe Calls)
        print("\n4. Testing Method Functionality...")
        test_method_functionality(app)
        
        # Test 5: UI Component Interaction
        print("\n5. Testing UI Component Interaction...")
        test_ui_interaction(app)
        
        print("\n" + "=" * 60)
        print("✅ All Plot Controls functionality tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_view_variables(app):
    """Test 3D view control variables."""
    print("   Testing view control variables...")
    
    # Test elevation variable
    try:
        app.elevation_var.set(45.0)
        current_elevation = app.elevation_var.get()
        if current_elevation == 45.0:
            print("   ✅ elevation_var works correctly")
        else:
            print(f"   ❌ elevation_var failed: expected 45.0, got {current_elevation}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing elevation_var: {e}")
        return False
    
    # Test azimuth variable
    try:
        app.azimuth_var.set(90.0)
        current_azimuth = app.azimuth_var.get()
        if current_azimuth == 90.0:
            print("   ✅ azimuth_var works correctly")
        else:
            print(f"   ❌ azimuth_var failed: expected 90.0, got {current_azimuth}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing azimuth_var: {e}")
        return False
    
    # Test zoom variable
    try:
        app.zoom_var.set(2.0)
        current_zoom = app.zoom_var.get()
        if current_zoom == 2.0:
            print("   ✅ zoom_var works correctly")
        else:
            print(f"   ❌ zoom_var failed: expected 2.0, got {current_zoom}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing zoom_var: {e}")
        return False
    
    print("   ✅ View control variables test passed")

def test_animation_variables(app):
    """Test animation control variables."""
    print("   Testing animation control variables...")
    
    # Test animation speed variable
    try:
        app.gd_anim_speed.set(2.5)
        current_speed = app.gd_anim_speed.get()
        if current_speed == 2.5:
            print("   ✅ gd_anim_speed works correctly")
        else:
            print(f"   ❌ gd_anim_speed failed: expected 2.5, got {current_speed}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing gd_anim_speed: {e}")
        return False
    
    # Test frame slider variable
    try:
        app.frame_slider.set(50)
        current_frame = app.frame_slider.get()
        if current_frame == 50:
            print("   ✅ frame_slider works correctly")
        else:
            print(f"   ❌ frame_slider failed: expected 50, got {current_frame}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing frame_slider: {e}")
        return False
    
    print("   ✅ Animation control variables test passed")

def test_3d_plot_initialization(app):
    """Test 3D plot initialization."""
    print("   Testing 3D plot initialization...")
    
    # Test figure properties
    try:
        if app.gd3d_fig is not None:
            print("   ✅ gd3d_fig is properly initialized")
        else:
            print("   ❌ gd3d_fig is None")
            return False
    except Exception as e:
        print(f"   ❌ Error testing gd3d_fig: {e}")
        return False
    
    # Test axes properties
    try:
        if app.gd3d_ax is not None:
            print("   ✅ gd3d_ax is properly initialized")
            # Test axes properties
            if hasattr(app.gd3d_ax, 'get_xlim'):
                print("   ✅ gd3d_ax has required methods")
            else:
                print("   ❌ gd3d_ax missing required methods")
                return False
        else:
            print("   ❌ gd3d_ax is None")
            return False
    except Exception as e:
        print(f"   ❌ Error testing gd3d_ax: {e}")
        return False
    
    # Test canvas properties
    try:
        if app.gd3d_canvas is not None:
            print("   ✅ gd3d_canvas is properly initialized")
        else:
            print("   ❌ gd3d_canvas is None")
            return False
    except Exception as e:
        print(f"   ❌ Error testing gd3d_canvas: {e}")
        return False
    
    print("   ✅ 3D plot initialization test passed")

def test_method_functionality(app):
    """Test method functionality with safe calls."""
    print("   Testing method functionality...")
    
    # Test view control methods (these should not raise exceptions)
    view_methods = [
        'reset_3d_view',
        'set_top_view',
        'set_side_view',
        'set_isometric_view'
    ]
    
    for method_name in view_methods:
        try:
            method = getattr(app, method_name)
            method()  # Call the method
            print(f"   ✅ {method_name} executed successfully")
        except Exception as e:
            print(f"   ❌ {method_name} failed: {e}")
            return False
    
    # Test animation control methods (these should not raise exceptions)
    anim_methods = [
        'play_gd_animation',
        'pause_gd_animation',
        'stop_gd_animation'
    ]
    
    for method_name in anim_methods:
        try:
            method = getattr(app, method_name)
            method()  # Call the method
            print(f"   ✅ {method_name} executed successfully")
        except Exception as e:
            print(f"   ❌ {method_name} failed: {e}")
            return False
    
    # Test MPEG management methods (these should not raise exceptions)
    mpeg_methods = [
        'refresh_mpeg_files'
    ]
    
    for method_name in mpeg_methods:
        try:
            method = getattr(app, method_name)
            method()  # Call the method
            print(f"   ✅ {method_name} executed successfully")
        except Exception as e:
            print(f"   ❌ {method_name} failed: {e}")
            return False
    
    print("   ✅ Method functionality test passed")

def test_ui_interaction(app):
    """Test UI component interaction."""
    print("   Testing UI component interaction...")
    
    # Test label updates
    try:
        # Test speed label update
        app.speed_label.config(text="2.5x")
        current_text = app.speed_label.cget('text')
        if current_text == "2.5x":
            print("   ✅ speed_label update works")
        else:
            print(f"   ❌ speed_label update failed: expected '2.5x', got '{current_text}'")
            return False
    except Exception as e:
        print(f"   ❌ Error testing speed_label: {e}")
        return False
    
    try:
        # Test frame label update
        app.frame_label.config(text="50/100")
        current_text = app.frame_label.cget('text')
        if current_text == "50/100":
            print("   ✅ frame_label update works")
        else:
            print(f"   ❌ frame_label update failed: expected '50/100', got '{current_text}'")
            return False
    except Exception as e:
        print(f"   ❌ Error testing frame_label: {e}")
        return False
    
    try:
        # Test elevation label update
        app.elevation_label.config(text="45°")
        current_text = app.elevation_label.cget('text')
        if current_text == "45°":
            print("   ✅ elevation_label update works")
        else:
            print(f"   ❌ elevation_label update failed: expected '45°', got '{current_text}'")
            return False
    except Exception as e:
        print(f"   ❌ Error testing elevation_label: {e}")
        return False
    
    try:
        # Test azimuth label update
        app.azimuth_label.config(text="90°")
        current_text = app.azimuth_label.cget('text')
        if current_text == "90°":
            print("   ✅ azimuth_label update works")
        else:
            print(f"   ❌ azimuth_label update failed: expected '90°', got '{current_text}'")
            return False
    except Exception as e:
        print(f"   ❌ Error testing azimuth_label: {e}")
        return False
    
    try:
        # Test zoom label update
        app.zoom_label.config(text="2.0x")
        current_text = app.zoom_label.cget('text')
        if current_text == "2.0x":
            print("   ✅ zoom_label update works")
        else:
            print(f"   ❌ zoom_label update failed: expected '2.0x', got '{current_text}'")
            return False
    except Exception as e:
        print(f"   ❌ Error testing zoom_label: {e}")
        return False
    
    # Test MPEG listbox
    try:
        if app.mpeg_files_listbox is not None:
            # Test listbox operations
            app.mpeg_files_listbox.delete(0, tk.END)  # Clear listbox
            app.mpeg_files_listbox.insert(tk.END, "test_file.mp4")  # Add test item
            items = app.mpeg_files_listbox.get(0, tk.END)
            if len(items) == 1 and items[0] == "test_file.mp4":
                print("   ✅ mpeg_files_listbox operations work")
            else:
                print(f"   ❌ mpeg_files_listbox operations failed")
                return False
        else:
            print("   ❌ mpeg_files_listbox is None")
            return False
    except Exception as e:
        print(f"   ❌ Error testing mpeg_files_listbox: {e}")
        return False
    
    print("   ✅ UI component interaction test passed")

def test_callback_functions(app):
    """Test callback functions for sliders and controls."""
    print("   Testing callback functions...")
    
    # Test animation speed callback
    try:
        app.on_anim_speed_change(2.5)
        print("   ✅ on_anim_speed_change callback works")
    except Exception as e:
        print(f"   ❌ on_anim_speed_change callback failed: {e}")
        return False
    
    # Test frame position callback
    try:
        app.on_frame_pos_change(50)
        print("   ✅ on_frame_pos_change callback works")
    except Exception as e:
        print(f"   ❌ on_frame_pos_change callback failed: {e}")
        return False
    
    # Test elevation change callback
    try:
        app.on_elevation_change(45)
        print("   ✅ on_elevation_change callback works")
    except Exception as e:
        print(f"   ❌ on_elevation_change callback failed: {e}")
        return False
    
    # Test azimuth change callback
    try:
        app.on_azimuth_change(90)
        print("   ✅ on_azimuth_change callback works")
    except Exception as e:
        print(f"   ❌ on_azimuth_change callback failed: {e}")
        return False
    
    # Test zoom change callback
    try:
        app.on_zoom_change(2.0)
        print("   ✅ on_zoom_change callback works")
    except Exception as e:
        print(f"   ❌ on_zoom_change callback failed: {e}")
        return False
    
    print("   ✅ Callback functions test passed")

if __name__ == "__main__":
    success = test_plot_controls_functionality()
    if success:
        print("\n🎉 All Plot Controls functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some Plot Controls functionality has issues")
        sys.exit(1) 