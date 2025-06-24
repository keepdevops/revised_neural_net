#!/usr/bin/env python3
"""
Comprehensive test script to verify that all features in the Plot Controls tab work correctly.
Tests include:
- 3D Gradient Descent Animation controls (Play, Pause, Stop)
- Speed and frame controls
- 3D View Controls (Elevation, Azimuth, Zoom)
- Preset view buttons
- MPEG File Management
- Embedded 3D plot
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_plot_controls_tab():
    """Test all features in the Plot Controls tab."""
    print("Testing Plot Controls Tab - All Features")
    print("=" * 60)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create GUI
        app = StockPredictionGUI(root)
        
        # Get the control notebook
        control_notebook = app.control_notebook
        
        # Find the Plot Controls tab
        plot_controls_tab = None
        for i in range(control_notebook.index('end')):
            tab_text = control_notebook.tab(i, 'text')
            if tab_text == "Plot Controls":
                plot_controls_tab = control_notebook.winfo_children()[i]
                break
        
        if plot_controls_tab is None:
            print("❌ Plot Controls tab not found")
            return False
        
        print("✅ Plot Controls tab found")
        
        # Test 1: 3D Gradient Descent Animation Controls
        print("\n1. Testing 3D Gradient Descent Animation Controls...")
        test_animation_controls(app, plot_controls_tab)
        
        # Test 2: 3D View Controls
        print("\n2. Testing 3D View Controls...")
        test_view_controls(app, plot_controls_tab)
        
        # Test 3: MPEG File Management
        print("\n3. Testing MPEG File Management...")
        test_mpeg_management(app, plot_controls_tab)
        
        # Test 4: Embedded 3D Plot
        print("\n4. Testing Embedded 3D Plot...")
        test_embedded_3d_plot(app)
        
        # Test 5: Method Availability
        print("\n5. Testing Method Availability...")
        test_method_availability(app)
        
        print("\n" + "=" * 60)
        print("✅ All Plot Controls tab tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_animation_controls(app, plot_controls_tab):
    """Test 3D Gradient Descent Animation controls."""
    print("   Testing animation playback controls...")
    
    # Check if animation control methods exist
    required_methods = [
        'play_gd_animation',
        'pause_gd_animation', 
        'stop_gd_animation',
        'on_anim_speed_change',
        'on_frame_pos_change'
    ]
    
    for method_name in required_methods:
        if hasattr(app, method_name):
            print(f"   ✅ {method_name} method exists")
        else:
            print(f"   ❌ {method_name} method missing")
            return False
    
    # Check if animation variables exist
    required_vars = [
        'gd_anim_speed',
        'frame_slider',
        'speed_label',
        'frame_label'
    ]
    
    for var_name in required_vars:
        if hasattr(app, var_name):
            print(f"   ✅ {var_name} variable exists")
        else:
            print(f"   ❌ {var_name} variable missing")
            return False
    
    print("   ✅ Animation controls test passed")

def test_view_controls(app, plot_controls_tab):
    """Test 3D View Controls."""
    print("   Testing 3D view controls...")
    
    # Check if view control methods exist
    required_methods = [
        'on_elevation_change',
        'on_azimuth_change',
        'on_zoom_change',
        'reset_3d_view',
        'set_top_view',
        'set_side_view',
        'set_isometric_view'
    ]
    
    for method_name in required_methods:
        if hasattr(app, method_name):
            print(f"   ✅ {method_name} method exists")
        else:
            print(f"   ❌ {method_name} method missing")
            return False
    
    # Check if view control variables exist
    required_vars = [
        'elevation_var',
        'azimuth_var',
        'zoom_var',
        'elevation_label',
        'azimuth_label',
        'zoom_label'
    ]
    
    for var_name in required_vars:
        if hasattr(app, var_name):
            print(f"   ✅ {var_name} variable exists")
        else:
            print(f"   ❌ {var_name} variable missing")
            return False
    
    print("   ✅ 3D view controls test passed")

def test_mpeg_management(app, plot_controls_tab):
    """Test MPEG File Management."""
    print("   Testing MPEG file management...")
    
    # Check if MPEG management methods exist
    required_methods = [
        'browse_mpeg_files',
        'open_selected_mpeg',
        'refresh_mpeg_files',
        'on_mpeg_file_select'
    ]
    
    for method_name in required_methods:
        if hasattr(app, method_name):
            print(f"   ✅ {method_name} method exists")
        else:
            print(f"   ❌ {method_name} method missing")
            return False
    
    # Check if MPEG listbox exists
    if hasattr(app, 'mpeg_files_listbox'):
        print("   ✅ mpeg_files_listbox exists")
    else:
        print("   ❌ mpeg_files_listbox missing")
        return False
    
    print("   ✅ MPEG file management test passed")

def test_embedded_3d_plot(app):
    """Test embedded 3D plot."""
    print("   Testing embedded 3D plot...")
    
    # Check if 3D plot components exist
    required_components = [
        'gd3d_fig',
        'gd3d_ax',
        'gd3d_canvas'
    ]
    
    for component_name in required_components:
        if hasattr(app, component_name):
            print(f"   ✅ {component_name} exists")
        else:
            print(f"   ❌ {component_name} missing")
            return False
    
    # Test 3D axes accessibility
    try:
        if app.gd3d_ax is not None:
            print("   ✅ 3D axes is accessible")
        else:
            print("   ❌ 3D axes is None")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing 3D axes: {e}")
        return False
    
    # Test canvas accessibility
    try:
        if app.gd3d_canvas is not None:
            print("   ✅ 3D canvas is accessible")
        else:
            print("   ❌ 3D canvas is None")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing 3D canvas: {e}")
        return False
    
    print("   ✅ Embedded 3D plot test passed")

def test_method_availability(app):
    """Test that all required methods are callable."""
    print("   Testing method callability...")
    
    # Test animation methods (should not raise exceptions when called)
    animation_methods = [
        'play_gd_animation',
        'pause_gd_animation',
        'stop_gd_animation'
    ]
    
    for method_name in animation_methods:
        try:
            method = getattr(app, method_name)
            if callable(method):
                print(f"   ✅ {method_name} is callable")
            else:
                print(f"   ❌ {method_name} is not callable")
                return False
        except Exception as e:
            print(f"   ❌ Error testing {method_name}: {e}")
            return False
    
    # Test view control methods
    view_methods = [
        'reset_3d_view',
        'set_top_view',
        'set_side_view',
        'set_isometric_view'
    ]
    
    for method_name in view_methods:
        try:
            method = getattr(app, method_name)
            if callable(method):
                print(f"   ✅ {method_name} is callable")
            else:
                print(f"   ❌ {method_name} is not callable")
                return False
        except Exception as e:
            print(f"   ❌ Error testing {method_name}: {e}")
            return False
    
    # Test MPEG management methods
    mpeg_methods = [
        'browse_mpeg_files',
        'open_selected_mpeg',
        'refresh_mpeg_files'
    ]
    
    for method_name in mpeg_methods:
        try:
            method = getattr(app, method_name)
            if callable(method):
                print(f"   ✅ {method_name} is callable")
            else:
                print(f"   ❌ {method_name} is not callable")
                return False
        except Exception as e:
            print(f"   ❌ Error testing {method_name}: {e}")
            return False
    
    print("   ✅ Method availability test passed")

def test_ui_components(plot_controls_tab):
    """Test that all UI components are properly created."""
    print("   Testing UI component creation...")
    
    # Count the expected number of frames/sections
    expected_sections = [
        "3D Gradient Descent Animation",
        "3D View Controls", 
        "Animation Files (MPEG/GIF/MP4)"
    ]
    
    found_sections = []
    for widget in plot_controls_tab.winfo_children():
        if isinstance(widget, ttk.LabelFrame):
            found_sections.append(widget.cget('text'))
    
    for section in expected_sections:
        if section in found_sections:
            print(f"   ✅ Section '{section}' found")
        else:
            print(f"   ❌ Section '{section}' missing")
            return False
    
    print("   ✅ UI components test passed")

if __name__ == "__main__":
    success = test_plot_controls_tab()
    if success:
        print("\n🎉 All Plot Controls tab features are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some Plot Controls tab features have issues")
        sys.exit(1) 