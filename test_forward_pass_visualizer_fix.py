#!/usr/bin/env python3
"""
Test script to verify the forward pass visualizer numpy array formatting fix.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import sys
import os

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_forward_pass_visualizer_formatting():
    """Test the forward pass visualizer with numpy arrays to verify formatting fix."""
    print("🧪 Testing Forward Pass Visualizer Numpy Array Formatting Fix")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("Forward Pass Visualizer Formatting Test")
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
        test_frame = ttk.LabelFrame(root, text="Formatting Test Controls", padding="10")
        test_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def test_scalar_values():
            """Test with scalar values."""
            print("🔢 Testing scalar values...")
            weights = 0.12345
            bias = 0.67890
            prediction = 100.54321
            input_data = 50.98765
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Scalar values test completed")
        
        def test_numpy_scalars():
            """Test with numpy scalar values."""
            print("🔢 Testing numpy scalar values...")
            weights = np.array(0.12345)
            bias = np.array(0.67890)
            prediction = np.array(100.54321)
            input_data = np.array(50.98765)
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Numpy scalar values test completed")
        
        def test_numpy_arrays():
            """Test with numpy arrays."""
            print("🔢 Testing numpy arrays...")
            weights = np.array([0.1, 0.2, 0.3, 0.4])
            bias = np.array([0.5])
            prediction = np.array([100.0])
            input_data = np.array([50.0, 60.0, 70.0, 80.0])
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Numpy arrays test completed")
        
        def test_mixed_types():
            """Test with mixed scalar and array types."""
            print("🔢 Testing mixed types...")
            weights = np.array([0.1, 0.2, 0.3, 0.4])
            bias = 0.5  # Scalar
            prediction = np.array([100.0])  # Array
            input_data = [50.0, 60.0, 70.0, 80.0]  # List
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            print("✅ Mixed types test completed")
        
        def test_multiple_updates():
            """Test multiple updates to stress test the formatting."""
            print("🔄 Testing multiple updates...")
            for i in range(10):
                weights = np.array([0.1 + i*0.01, 0.2 + i*0.005, 0.3 - i*0.002, 0.4 + i*0.003])
                bias = np.array([0.5 + i*0.01])
                prediction = np.array([100.0 + i*0.5])
                input_data = np.array([50.0 + i, 60.0 + i*0.8, 70.0 + i*0.6, 80.0 + i*0.4])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.1)
            
            print("✅ Multiple updates test completed")
        
        def clear_data():
            """Clear all visualization data."""
            print("🗑️ Clearing visualization data...")
            visualizer.clear_visualization()
            print("✅ Data cleared")
        
        # Create buttons for each test
        ttk.Button(test_frame, text="Test Scalars", command=test_scalar_values).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Numpy Scalars", command=test_numpy_scalars).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Numpy Arrays", command=test_numpy_arrays).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Mixed Types", command=test_mixed_types).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Test Multiple Updates", command=test_multiple_updates).pack(side="left", padx=5)
        ttk.Button(test_frame, text="Clear Data", command=clear_data).pack(side="left", padx=5)
        
        # Add instructions
        instructions = ttk.Label(
            root, 
            text="Click the buttons above to test different data types.\nThe visualizer should handle all formats without formatting errors.",
            font=("Arial", 10),
            foreground="blue"
        )
        instructions.pack(pady=10)
        
        print("\n📋 Test Instructions:")
        print("1. Click 'Test Scalars' to test with regular Python scalars")
        print("2. Click 'Test Numpy Scalars' to test with numpy scalar arrays")
        print("3. Click 'Test Numpy Arrays' to test with numpy arrays")
        print("4. Click 'Test Mixed Types' to test with mixed data types")
        print("5. Click 'Test Multiple Updates' to stress test the formatting")
        print("6. Watch the info display at the bottom for formatting errors")
        print("7. Check the console for any error messages")
        
        print("\n✅ Forward pass visualizer formatting test ready!")
        print("🎯 The visualizer should now handle numpy arrays without formatting errors.")
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_forward_pass_visualizer_formatting()
    if success:
        print("\n🎉 Forward pass visualizer formatting test completed successfully!")
    else:
        print("\n💥 Forward pass visualizer formatting test failed!")
        sys.exit(1) 