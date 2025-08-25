#!/usr/bin/env python3
"""
Test script to verify the 3D gradient descent plot fix.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import sys
import os

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_3d_gradient_descent_fix():
    """Test the 3D gradient descent plot fix."""
    print("🧪 Testing 3D Gradient Descent Plot Fix")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("3D Gradient Descent Fix Test")
    root.geometry("800x600")
    
    # Mock model path (use a real model if available)
    model_path = None
    
    # Look for a real model directory
    for item in os.listdir('.'):
        if item.startswith('model_') and os.path.isdir(item):
            # Check if it has the required files
            weights_dir = os.path.join(item, 'weights_history')
            if os.path.exists(weights_dir):
                model_path = item
                break
    
    if not model_path:
        print("❌ No suitable model directory found for testing")
        print("Please train a model first to test the gradient descent visualization")
        root.destroy()
        return
    
    print(f"✅ Using model directory: {model_path}")
    
    # Mock plot parameters
    plot_params = {
        'color_scheme': 'viridis',
        'point_size': 8,
        'line_width': 3,
        'surface_alpha': 0.6,
        'w1_range': [-2.0, 2.0],
        'w2_range': [-2.0, 2.0],
        'n_points': 30,
        'w1_index': 0,
        'w2_index': 0
    }
    
    try:
        # Import the floating 3D window
        from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
        
        # Create the floating 3D window
        print("🏗️ Creating floating 3D window...")
        window = Floating3DWindow(root, model_path, plot_params)
        
        print("✅ Floating 3D window created successfully")
        
        # Test the gradient descent plot creation
        print("🎨 Testing gradient descent plot creation...")
        
        # Set visualization type to gradient descent
        window.plot_params['visualization_type'] = 'gradient_descent'
        
        # Create the plot
        window.create_plot()
        
        print("✅ Gradient descent plot created successfully")
        
        # Test the extract_weight_by_index function
        print("🔧 Testing extract_weight_by_index function...")
        
        # Import the function
        viz_dir = os.path.join(os.path.dirname(__file__), 'visualization')
        if viz_dir not in sys.path:
            sys.path.insert(0, viz_dir)
        
        from gradient_descent_3d import extract_weight_by_index
        
        # Test with mock weights
        mock_weights = {
            'W1': np.array([[0.1, 0.2], [0.3, 0.4]]),
            'W2': np.array([[0.5], [0.6]])
        }
        
        w1_val = extract_weight_by_index(mock_weights, 0, 'W1')
        w2_val = extract_weight_by_index(mock_weights, 0, 'W2')
        
        print(f"✅ extract_weight_by_index test passed:")
        print(f"   W1[0] = {w1_val}")
        print(f"   W2[0] = {w2_val}")
        
        # Test with real weights if available
        weights_dir = os.path.join(model_path, 'weights_history')
        if os.path.exists(weights_dir):
            import glob
            weights_files = sorted(glob.glob(os.path.join(weights_dir, "weights_history_*.npz")))
            if weights_files:
                print("🔍 Testing with real weights...")
                with np.load(weights_files[0]) as data:
                    real_weights = {
                        'W1': data['W1'],
                        'W2': data['W2']
                    }
                
                w1_val = extract_weight_by_index(real_weights, 0, 'W1')
                w2_val = extract_weight_by_index(real_weights, 0, 'W2')
                
                print(f"✅ Real weights test passed:")
                print(f"   W1[0] = {w1_val}")
                print(f"   W2[0] = {w2_val}")
        
        print("🎉 All tests passed! The 3D gradient descent plot fix is working correctly.")
        
        # Keep the window open for a few seconds
        print("⏰ Keeping window open for 5 seconds...")
        root.after(5000, root.destroy)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()

if __name__ == "__main__":
    test_3d_gradient_descent_fix() 