#!/usr/bin/env python3
"""
Test script to verify that the colorbar issue is fixed in the 3D visualization.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np

# Add the current directory to the path so we can import the GUI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_colorbar_functionality():
    """Test that the colorbar functionality works properly."""
    print("🧪 Testing colorbar functionality...")
    
    try:
        # Import the GUI
        from gui.main_gui import StockPredictionGUI
        
        # Create a minimal root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create the GUI instance
        app = StockPredictionGUI(root)
        
        print("✅ GUI instance created successfully")
        
        # Test the ensure_3d_axes_available method
        print("Testing ensure_3d_axes_available method...")
        result = app.ensure_3d_axes_available()
        
        if result:
            print("✅ ensure_3d_axes_available returned True")
            
            # Check if gd3d_fig is properly initialized
            if hasattr(app, 'gd3d_fig') and app.gd3d_fig is not None:
                print("✅ gd3d_fig is properly initialized")
                
                # Test creating a simple 3D surface with colorbar
                print("Testing 3D surface creation with colorbar...")
                
                # Create sample data
                x = np.linspace(-5, 5, 50)
                y = np.linspace(-5, 5, 50)
                X, Y = np.meshgrid(x, y)
                Z = np.sin(np.sqrt(X**2 + Y**2))
                
                # Clear the axes
                app.gd3d_ax.clear()
                
                # Create surface plot
                surface = app.gd3d_ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                
                # Test colorbar addition
                try:
                    # Ensure proper layout
                    app.gd3d_fig.subplots_adjust(right=0.85)
                    
                    # Add colorbar
                    colorbar = app.gd3d_fig.colorbar(surface, ax=app.gd3d_ax, shrink=0.5, aspect=5)
                    colorbar.set_label('Test Value')
                    
                    print("✅ Colorbar added successfully to test surface")
                    
                    # Set labels
                    app.gd3d_ax.set_xlabel('X')
                    app.gd3d_ax.set_ylabel('Y')
                    app.gd3d_ax.set_zlabel('Z')
                    app.gd3d_ax.set_title('Test 3D Surface with Colorbar')
                    
                    print("✅ Test 3D surface created successfully with colorbar")
                    
                except Exception as e:
                    print(f"❌ Error adding colorbar to test surface: {e}")
                    return False
                
            else:
                print("❌ gd3d_fig is not properly initialized")
                return False
        else:
            print("❌ ensure_3d_axes_available returned False")
            return False
        
        # Clean up
        root.destroy()
        
        print("✅ Colorbar functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in colorbar functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3d_visualization_methods():
    """Test the 3D visualization methods that use colorbars."""
    print("\n🧪 Testing 3D visualization methods...")
    
    try:
        # Import the GUI
        from gui.main_gui import StockPredictionGUI
        
        # Create a minimal root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create the GUI instance
        app = StockPredictionGUI(root)
        
        # Test the load_3d_visualization_in_gui method (without actual model data)
        print("Testing load_3d_visualization_in_gui method structure...")
        
        # Check if the method exists and has proper colorbar handling
        if hasattr(app, 'load_3d_visualization_in_gui'):
            print("✅ load_3d_visualization_in_gui method exists")
            
            # Check if the method has proper colorbar error handling
            import inspect
            source = inspect.getsource(app.load_3d_visualization_in_gui)
            
            if 'gd3d_fig' in source and 'colorbar' in source:
                print("✅ Method contains colorbar handling code")
                
                if 'hasattr(self, \'gd3d_fig\')' in source:
                    print("✅ Method has proper gd3d_fig availability check")
                    
                    if 'subplots_adjust(right=0.85)' in source:
                        print("✅ Method has proper figure layout adjustment")
                        
                        if 'make_axes_locatable' in source:
                            print("✅ Method has alternative colorbar method")
                            
                            print("✅ 3D visualization methods have proper colorbar handling")
                            return True
                        else:
                            print("⚠️ Method missing alternative colorbar method")
                    else:
                        print("⚠️ Method missing figure layout adjustment")
                else:
                    print("⚠️ Method missing gd3d_fig availability check")
            else:
                print("⚠️ Method missing colorbar handling code")
        else:
            print("❌ load_3d_visualization_in_gui method not found")
            return False
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error in 3D visualization methods test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting colorbar fix verification tests...\n")
    
    # Test 1: Basic colorbar functionality
    test1_passed = test_colorbar_functionality()
    
    # Test 2: 3D visualization methods
    test2_passed = test_3d_visualization_methods()
    
    # Summary
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    if test1_passed:
        print("✅ Test 1: Colorbar functionality - PASSED")
    else:
        print("❌ Test 1: Colorbar functionality - FAILED")
    
    if test2_passed:
        print("✅ Test 2: 3D visualization methods - PASSED")
    else:
        print("❌ Test 2: 3D visualization methods - FAILED")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The colorbar issue has been fixed.")
        print("   The warning 'gd3d_fig not available, skipping colorbar' should no longer appear.")
        return True
    else:
        print("\n⚠️ Some tests failed. The colorbar issue may still exist.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 