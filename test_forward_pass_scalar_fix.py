#!/usr/bin/env python3
"""
Test script to verify the forward pass visualizer scalar conversion fix.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import sys
import os

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_forward_pass_scalar_fix():
    """Test the forward pass visualizer scalar conversion with various array sizes."""
    print("🧪 Testing Forward Pass Visualizer Scalar Conversion Fix")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("Forward Pass Visualizer Scalar Fix Test")
    root.geometry("800x600")
    
    # Mock app
    class MockApp:
        pass
    
    app = MockApp()
    
    try:
        # Import the forward pass visualizer
        from stock_prediction_gui.ui.widgets.forward_pass_visualizer import ForwardPassVisualizer
        
        # Create the visualizer
        print("📊 Creating forward pass visualizer...")
        visualizer = ForwardPassVisualizer(root, app)
        visualizer.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        print("✅ Forward pass visualizer created successfully!")
        
        # Add test controls
        test_frame = ttk.LabelFrame(root, text="Scalar Conversion Test Controls", padding="10")
        test_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def test_single_element_arrays():
            """Test scalar conversion with single-element arrays."""
            print("🔢 Testing scalar conversion with single-element arrays...")
            visualizer.clear_visualization()
            
            for i in range(10):
                weights = np.array([0.1 + i * 0.01])  # Single element
                bias = np.array([0.5 + i * 0.02])     # Single element
                prediction = np.array([100.0 + i * 2.0])  # Single element
                input_data = np.array([50.0 + i * 1.5])   # Single element
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ Single-element arrays test completed")
        
        def test_multi_element_arrays():
            """Test scalar conversion with multi-element arrays."""
            print("🔢 Testing scalar conversion with multi-element arrays...")
            visualizer.clear_visualization()
            
            for i in range(10):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01, 0.6 + i * 0.008])
                prediction = np.array([100.0 + i * 2.0, 101.0 + i * 2.1, 102.0 + i * 2.2])
                input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ Multi-element arrays test completed")
        
        def test_mixed_array_sizes():
            """Test scalar conversion with mixed array sizes."""
            print("🔢 Testing scalar conversion with mixed array sizes...")
            visualizer.clear_visualization()
            
            for i in range(10):
                if i % 3 == 0:
                    # Single element arrays
                    weights = np.array([0.1 + i * 0.01])
                    bias = np.array([0.5 + i * 0.02])
                    prediction = np.array([100.0 + i * 2.0])
                    input_data = np.array([50.0 + i * 1.5])
                elif i % 3 == 1:
                    # Multi-element arrays
                    weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002])
                    bias = np.array([0.5 + i * 0.01, 0.6 + i * 0.008])
                    prediction = np.array([100.0 + i * 2.0, 101.0 + i * 2.1])
                    input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8])
                else:
                    # Mixed types
                    weights = 0.1 + i * 0.01  # Scalar
                    bias = np.array([0.5 + i * 0.01, 0.6 + i * 0.008])  # Array
                    prediction = np.array([100.0 + i * 2.0])  # Single element
                    input_data = [50.0 + i * 1.5, 60.0 + i * 1.2]  # List
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ Mixed array sizes test completed")
        
        def test_empty_arrays():
            """Test scalar conversion with empty arrays."""
            print("🔢 Testing scalar conversion with empty arrays...")
            visualizer.clear_visualization()
            
            # Add some data first
            for i in range(5):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01])
                prediction = np.array([100.0 + i * 2.0])
                input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            # Then add empty arrays
            weights = np.array([])
            bias = np.array([])
            prediction = np.array([])
            input_data = np.array([])
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Empty arrays test completed")
        
        def test_2d_arrays():
            """Test scalar conversion with 2D arrays."""
            print("🔢 Testing scalar conversion with 2D arrays...")
            visualizer.clear_visualization()
            
            for i in range(10):
                weights = np.array([[0.1 + i * 0.01, 0.2 + i * 0.005], [0.3 - i * 0.002, 0.4 + i * 0.003]])
                bias = np.array([[0.5 + i * 0.01], [0.6 + i * 0.008]])
                prediction = np.array([[100.0 + i * 2.0, 101.0 + i * 2.1], [102.0 + i * 2.2, 103.0 + i * 2.3]])
                input_data = np.array([[50.0 + i * 1.5, 60.0 + i * 1.2], [70.0 + i * 0.8, 80.0 + i * 0.5]])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ 2D arrays test completed")
        
        def test_nan_inf_arrays():
            """Test scalar conversion with NaN/Inf arrays."""
            print("🔢 Testing scalar conversion with NaN/Inf arrays...")
            visualizer.clear_visualization()
            
            for i in range(10):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01])
                
                # Add some NaN/Inf values
                if i % 3 == 0:
                    prediction = np.array([np.nan, 101.0 + i * 2.1, 102.0 + i * 2.2])
                    input_data = np.array([50.0 + i * 1.5, np.inf, 70.0 + i * 0.8, 80.0 + i * 0.5])
                else:
                    prediction = np.array([100.0 + i * 2.0, 101.0 + i * 2.1, 102.0 + i * 2.2])
                    input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ NaN/Inf arrays test completed")
        
        def clear_data():
            """Clear all visualization data."""
            print("🗑️ Clearing visualization data...")
            visualizer.clear_visualization()
            print("✅ Data cleared")
        
        # Create buttons for each test
        ttk.Button(test_frame, text="Test Single Element Arrays", command=test_single_element_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Multi Element Arrays", command=test_multi_element_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Mixed Array Sizes", command=test_mixed_array_sizes).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Empty Arrays", command=test_empty_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test 2D Arrays", command=test_2d_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test NaN/Inf Arrays", command=test_nan_inf_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Clear Data", command=clear_data).pack(side="left", padx=5)
        
        # Add instructions
        instructions = ttk.Label(
            root, 
            text="Click the buttons above to test scalar conversion with different array sizes.\nThe visualizer should handle all array sizes without scalar conversion errors.",
            font=("Arial", 10),
            foreground="blue"
        )
        instructions.pack(pady=10)
        
        print("\n📋 Test Instructions:")
        print("1. Click 'Test Single Element Arrays' to test with single-element numpy arrays")
        print("2. Click 'Test Multi Element Arrays' to test with multi-element numpy arrays")
        print("3. Click 'Test Mixed Array Sizes' to test with mixed array sizes")
        print("4. Click 'Test Empty Arrays' to test with empty arrays")
        print("5. Click 'Test 2D Arrays' to test with 2D numpy arrays")
        print("6. Click 'Test NaN/Inf Arrays' to test with arrays containing NaN/Inf values")
        print("7. Watch the info display and check for any error messages")
        print("8. Check the console for any error messages")
        
        print("\n✅ Forward pass visualizer scalar conversion test ready!")
        print("🎯 The visualizer should now handle all array sizes without scalar conversion errors.")
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_forward_pass_scalar_fix()
    if success:
        print("\n🎉 Forward pass visualizer scalar conversion test completed successfully!")
    else:
        print("\n💥 Forward pass visualizer scalar conversion test failed!")
        sys.exit(1) 