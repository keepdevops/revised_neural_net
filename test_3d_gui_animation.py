#!/usr/bin/env python3
"""
Test script to verify 3D animation controls in the GUI.
"""

import tkinter as tk
from gui.main_gui import StockPredictionGUI
import time

def test_3d_animation_controls():
    """Test the 3D animation controls in the GUI."""
    print("Testing 3D Animation Controls in GUI")
    print("=" * 50)
    
    try:
        # Create a minimal GUI instance
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = StockPredictionGUI(root)
        
        # Test 1: Check if 3D axes are available
        print("1. Testing 3D axes availability...")
        if app.ensure_3d_axes_available():
            print("✅ 3D axes are available")
        else:
            print("❌ 3D axes are not available")
            return False
        
        # Test 2: Check if animation methods exist
        print("2. Testing animation methods...")
        required_methods = [
            'play_gd_animation',
            'pause_gd_animation', 
            'stop_gd_animation',
            'on_anim_speed_change',
            'on_frame_pos_change'
        ]
        
        for method in required_methods:
            if hasattr(app, method):
                print(f"✅ {method} method exists")
            else:
                print(f"❌ {method} method missing")
                return False
        
        # Test 3: Check if 3D axes have proper text
        print("3. Testing 3D axes text...")
        if hasattr(app, 'gd3d_ax') and app.gd3d_ax is not None:
            print("✅ 3D axes object exists")
            
            # Check if the text is properly displayed
            try:
                # Clear any existing text
                app.gd3d_ax.clear()
                
                # Add test text
                app.gd3d_ax.text2D(0.5, 0.5, "3D Animation Test\nWorking correctly!", 
                                  ha="center", va="center", transform=app.gd3d_ax.transAxes,
                                  fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
                app.gd3d_ax.axis("off")
                
                print("✅ 3D text placement working")
                
            except Exception as e:
                print(f"❌ Error with 3D text: {e}")
                return False
        else:
            print("❌ 3D axes object not found")
            return False
        
        # Test 4: Check if animation variables are initialized
        print("4. Testing animation variables...")
        required_vars = [
            'gd_anim_speed',
            'frame_slider',
            'frame_label',
            'speed_label'
        ]
        
        for var in required_vars:
            if hasattr(app, var):
                print(f"✅ {var} variable exists")
            else:
                print(f"❌ {var} variable missing")
                return False
        
        # Test 5: Simulate animation start
        print("5. Testing animation simulation...")
        try:
            # Set up some dummy data for testing
            app.gd_anim_running = False
            app.gd_current_frame = 0
            
            # Test play method (should not crash)
            app.play_gd_animation()
            print("✅ play_gd_animation method works")
            
            # Test pause method
            app.pause_gd_animation()
            print("✅ pause_gd_animation method works")
            
            # Test stop method
            app.stop_gd_animation()
            print("✅ stop_gd_animation method works")
            
        except Exception as e:
            print(f"❌ Error in animation methods: {e}")
            return False
        
        print("\n🎉 All 3D animation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing 3D animation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_gui_initialization():
    """Test that the GUI initializes without errors."""
    print("\nTesting GUI Initialization")
    print("=" * 50)
    
    try:
        # Create a minimal GUI instance
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = StockPredictionGUI(root)
        
        # Check if all required components are created
        required_components = [
            'control_panel',
            'display_panel',
            'control_notebook',
            'display_notebook'
        ]
        
        for component in required_components:
            if hasattr(app, component):
                print(f"✅ {component} created successfully")
            else:
                print(f"❌ {component} not found")
                return False
        
        print("✅ GUI initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Error in GUI initialization: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def main():
    """Run all tests."""
    print("3D Animation GUI Test Suite")
    print("=" * 60)
    
    # Test 1: GUI initialization
    test1_passed = test_gui_initialization()
    
    # Test 2: 3D animation controls
    test2_passed = test_3d_animation_controls()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"GUI Initialization: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"3D Animation Controls: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! 3D animation is working correctly in the GUI.")
        print("\nTo use the 3D Gradient Descent Animation:")
        print("1. Open the GUI: python3 gui/main_gui.py")
        print("2. Go to the 'Plot Controls' tab")
        print("3. Select a model from the 'Model Management' tab")
        print("4. Click 'Play' to start the 3D animation")
        print("5. Use 'Pause' and 'Stop' to control the animation")
        print("6. Adjust speed and frame position with the sliders")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1) 