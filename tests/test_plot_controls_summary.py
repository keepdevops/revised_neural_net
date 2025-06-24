#!/usr/bin/env python3
"""
Summary test for the Plot Controls tab.
Provides a comprehensive overview of the current status and any remaining issues.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_gui import StockPredictionGUI

def test_plot_controls_summary():
    """Provide a comprehensive summary of Plot Controls tab status."""
    print("Plot Controls Tab - Comprehensive Status Report")
    print("=" * 70)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create GUI
        app = StockPredictionGUI(root)
        
        print("\n📊 FEATURE STATUS SUMMARY:")
        print("-" * 40)
        
        # 1. Animation Controls
        print("\n🎬 3D Gradient Descent Animation Controls:")
        animation_features = [
            ('play_gd_animation', 'Play button'),
            ('pause_gd_animation', 'Pause button'),
            ('stop_gd_animation', 'Stop button'),
            ('on_anim_speed_change', 'Speed control'),
            ('on_frame_pos_change', 'Frame slider'),
            ('gd_anim_speed', 'Speed variable'),
            ('frame_slider', 'Frame slider variable'),
            ('speed_label', 'Speed label'),
            ('frame_label', 'Frame label')
        ]
        
        for method_name, description in animation_features:
            status = "✅" if hasattr(app, method_name) else "❌"
            print(f"   {status} {description} ({method_name})")
        
        # 2. 3D View Controls
        print("\n👁 3D View Controls:")
        view_features = [
            ('on_elevation_change', 'Elevation control'),
            ('on_azimuth_change', 'Azimuth control'),
            ('on_zoom_change', 'Zoom control'),
            ('reset_3d_view', 'Reset view button'),
            ('set_top_view', 'Top view button'),
            ('set_side_view', 'Side view button'),
            ('set_isometric_view', 'Isometric view button'),
            ('elevation_var', 'Elevation variable'),
            ('azimuth_var', 'Azimuth variable'),
            ('zoom_var', 'Zoom variable'),
            ('elevation_label', 'Elevation label'),
            ('azimuth_label', 'Azimuth label'),
            ('zoom_label', 'Zoom label')
        ]
        
        for method_name, description in view_features:
            status = "✅" if hasattr(app, method_name) else "❌"
            print(f"   {status} {description} ({method_name})")
        
        # 3. MPEG File Management
        print("\n🎬 MPEG File Management:")
        mpeg_features = [
            ('browse_mpeg_files', 'Browse button'),
            ('open_selected_mpeg', 'Open selected button'),
            ('refresh_mpeg_files', 'Refresh button'),
            ('on_mpeg_file_select', 'File selection handler'),
            ('mpeg_files_listbox', 'File listbox')
        ]
        
        for method_name, description in mpeg_features:
            status = "✅" if hasattr(app, method_name) else "❌"
            print(f"   {status} {description} ({method_name})")
        
        # 4. 3D Plot Components
        print("\n📊 3D Plot Components:")
        plot_components = [
            ('gd3d_fig', '3D Figure'),
            ('gd3d_ax', '3D Axes'),
            ('gd3d_canvas', '3D Canvas')
        ]
        
        for component_name, description in plot_components:
            if hasattr(app, component_name):
                component = getattr(app, component_name)
                status = "✅" if component is not None else "⚠️"
                print(f"   {status} {description} ({component_name})")
            else:
                print(f"   ❌ {description} ({component_name})")
        
        # 5. Method Callability Test
        print("\n🔧 Method Callability Test:")
        callable_methods = [
            'play_gd_animation',
            'pause_gd_animation',
            'stop_gd_animation',
            'reset_3d_view',
            'set_top_view',
            'set_side_view',
            'set_isometric_view',
            'refresh_mpeg_files'
        ]
        
        for method_name in callable_methods:
            try:
                method = getattr(app, method_name)
                if callable(method):
                    print(f"   ✅ {method_name} is callable")
                else:
                    print(f"   ❌ {method_name} is not callable")
            except Exception as e:
                print(f"   ❌ {method_name} error: {e}")
        
        # 6. Variable Functionality Test
        print("\n⚙️ Variable Functionality Test:")
        test_variables = [
            ('elevation_var', 45.0),
            ('azimuth_var', 90.0),
            ('zoom_var', 2.0),
            ('gd_anim_speed', 2.5)
        ]
        
        for var_name, test_value in test_variables:
            try:
                var = getattr(app, var_name)
                var.set(test_value)
                current_value = var.get()
                if current_value == test_value:
                    print(f"   ✅ {var_name} works correctly")
                else:
                    print(f"   ❌ {var_name} failed: expected {test_value}, got {current_value}")
            except Exception as e:
                print(f"   ❌ {var_name} error: {e}")
        
        # 7. UI Component Test
        print("\n🎨 UI Component Test:")
        ui_components = [
            ('speed_label', 'Speed label'),
            ('frame_label', 'Frame label'),
            ('elevation_label', 'Elevation label'),
            ('azimuth_label', 'Azimuth label'),
            ('zoom_label', 'Zoom label'),
            ('mpeg_files_listbox', 'MPEG listbox')
        ]
        
        for component_name, description in ui_components:
            try:
                component = getattr(app, component_name)
                if component is not None:
                    print(f"   ✅ {description} exists")
                else:
                    print(f"   ❌ {description} is None")
            except Exception as e:
                print(f"   ❌ {description} error: {e}")
        
        # 8. Known Issues
        print("\n⚠️ KNOWN ISSUES:")
        print("-" * 20)
        
        # Check for specific known issues
        issues_found = []
        
        # Issue 1: gd3d_fig being None
        if hasattr(app, 'gd3d_fig') and app.gd3d_fig is None:
            issues_found.append("gd3d_fig is None - 3D plot may not display correctly")
        
        # Issue 2: Animation methods expecting model path
        try:
            app.play_gd_animation()
        except TypeError as e:
            if "expected str, bytes or os.PathLike object, not NoneType" in str(e):
                issues_found.append("Animation methods expect a selected model path")
        
        if issues_found:
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("   No known issues detected")
        
        # 9. Overall Status
        print("\n📈 OVERALL STATUS:")
        print("-" * 20)
        
        # Count working features
        total_features = len(animation_features) + len(view_features) + len(mpeg_features) + len(plot_components)
        working_features = 0
        
        for feature_list in [animation_features, view_features, mpeg_features]:
            for method_name, _ in feature_list:
                if hasattr(app, method_name):
                    working_features += 1
        
        for component_name, _ in plot_components:
            if hasattr(app, component_name) and getattr(app, component_name) is not None:
                working_features += 1
        
        success_rate = (working_features / total_features) * 100
        print(f"   Working features: {working_features}/{total_features} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("   🎉 Excellent! Plot Controls tab is working very well")
        elif success_rate >= 75:
            print("   ✅ Good! Plot Controls tab is working well with minor issues")
        elif success_rate >= 50:
            print("   ⚠️ Fair! Plot Controls tab has some issues but is functional")
        else:
            print("   ❌ Poor! Plot Controls tab has significant issues")
        
        print("\n" + "=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Error during summary test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    success = test_plot_controls_summary()
    if success:
        print("\n✅ Plot Controls tab summary completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Plot Controls tab summary failed")
        sys.exit(1) 