#!/usr/bin/env python3
"""
Test script to verify the forward pass visualizer polynomial fitting fix.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import sys
import os

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_forward_pass_polynomial_fix():
    """Test the forward pass visualizer polynomial fitting with various data types."""
    print("🧪 Testing Forward Pass Visualizer Polynomial Fitting Fix")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("Forward Pass Visualizer Polynomial Fix Test")
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
        test_frame = ttk.LabelFrame(root, text="Polynomial Fitting Test Controls", padding="10")
        test_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def test_scalar_polynomial():
            """Test polynomial fitting with scalar values."""
            print("🔢 Testing polynomial fitting with scalar values...")
            visualizer.clear_visualization()
            
            for i in range(20):
                weights = 0.1 + i * 0.01
                bias = 0.5 + i * 0.02
                prediction = 100.0 + i * 2.0 + np.random.randn() * 0.1
                input_data = 50.0 + i * 1.5
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            print("✅ Scalar polynomial test completed")
        
        def test_numpy_scalar_polynomial():
            """Test polynomial fitting with numpy scalar arrays."""
            print("🔢 Testing polynomial fitting with numpy scalar arrays...")
            visualizer.clear_visualization()
            
            for i in range(20):
                weights = np.array(0.1 + i * 0.01)
                bias = np.array(0.5 + i * 0.02)
                prediction = np.array(100.0 + i * 2.0 + np.random.randn() * 0.1)
                input_data = np.array(50.0 + i * 1.5)
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            print("✅ Numpy scalar polynomial test completed")
        
        def test_numpy_array_polynomial():
            """Test polynomial fitting with numpy arrays."""
            print("🔢 Testing polynomial fitting with numpy arrays...")
            visualizer.clear_visualization()
            
            for i in range(20):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01])
                prediction = np.array([100.0 + i * 2.0 + np.random.randn() * 0.1])
                input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            print("✅ Numpy array polynomial test completed")
        
        def test_mixed_types_polynomial():
            """Test polynomial fitting with mixed data types."""
            print("🔢 Testing polynomial fitting with mixed data types...")
            visualizer.clear_visualization()
            
            for i in range(20):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = 0.5 + i * 0.01  # Scalar
                prediction = np.array([100.0 + i * 2.0 + np.random.randn() * 0.1])  # Array
                input_data = [50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5]  # List
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            print("✅ Mixed types polynomial test completed")
        
        def test_nan_inf_polynomial():
            """Test polynomial fitting with NaN/Inf values."""
            print("🔢 Testing polynomial fitting with NaN/Inf values...")
            visualizer.clear_visualization()
            
            for i in range(20):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01])
                
                # Add some NaN/Inf values
                if i % 5 == 0:
                    prediction = np.array([np.nan])
                    input_data = np.array([np.inf])
                else:
                    prediction = np.array([100.0 + i * 2.0 + np.random.randn() * 0.1])
                    input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            print("✅ NaN/Inf polynomial test completed")
        
        def test_empty_data_polynomial():
            """Test polynomial fitting with empty data."""
            print("🔢 Testing polynomial fitting with empty data...")
            visualizer.clear_visualization()
            
            # Add some data first
            for i in range(5):
                weights = np.array([0.1 + i * 0.01, 0.2 + i * 0.005, 0.3 - i * 0.002, 0.4 + i * 0.003])
                bias = np.array([0.5 + i * 0.01])
                prediction = np.array([100.0 + i * 2.0])
                input_data = np.array([50.0 + i * 1.5, 60.0 + i * 1.2, 70.0 + i * 0.8, 80.0 + i * 0.5])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
            
            # Then add empty data
            weights = np.array([])
            bias = np.array([])
            prediction = np.array([])
            input_data = np.array([])
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Empty data polynomial test completed")
        
        def clear_data():
            """Clear all visualization data."""
            print("🗑️ Clearing visualization data...")
            visualizer.clear_visualization()
            print("✅ Data cleared")
        
        # Create buttons for each test
        ttk.Button(test_frame, text="Test Scalar Polynomial", command=test_scalar_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Numpy Scalar Polynomial", command=test_numpy_scalar_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Numpy Array Polynomial", command=test_numpy_array_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Mixed Types Polynomial", command=test_mixed_types_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test NaN/Inf Polynomial", command=test_nan_inf_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Empty Data Polynomial", command=test_empty_data_polynomial).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Clear Data", command=clear_data).pack(side="left", padx=5)
        
        # Add instructions
        instructions = ttk.Label(
            root, 
            text="Click the buttons above to test polynomial fitting with different data types.\nThe visualizer should handle all formats without polynomial fitting errors.",
            font=("Arial", 10),
            foreground="blue"
        )
        instructions.pack(pady=10)
        
        print("\n📋 Test Instructions:")
        print("1. Click 'Test Scalar Polynomial' to test with regular Python scalars")
        print("2. Click 'Test Numpy Scalar Polynomial' to test with numpy scalar arrays")
        print("3. Click 'Test Numpy Array Polynomial' to test with numpy arrays")
        print("4. Click 'Test Mixed Types Polynomial' to test with mixed data types")
        print("5. Click 'Test NaN/Inf Polynomial' to test with invalid numeric values")
        print("6. Click 'Test Empty Data Polynomial' to test with empty data")
        print("7. Watch the prediction plot for trend lines and check for errors")
        print("8. Check the console for any error messages")
        
        print("\n✅ Forward pass visualizer polynomial fitting test ready!")
        print("🎯 The visualizer should now handle all data types without polynomial fitting errors.")
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_forward_pass_polynomial_fix()
    if success:
        print("\n🎉 Forward pass visualizer polynomial fitting test completed successfully!")
    else:
        print("\n💥 Forward pass visualizer polynomial fitting test failed!")
        sys.exit(1) 