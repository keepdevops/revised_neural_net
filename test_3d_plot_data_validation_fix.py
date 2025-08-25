#!/usr/bin/env python3
"""
Test script to verify the 3D plot data validation fix.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import time
import sys
import os

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

def test_3d_plot_data_validation_fix():
    """Test the 3D plot data validation fix with mixed data types."""
    print("🧪 Testing 3D Plot Data Validation Fix")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("3D Plot Data Validation Fix Test")
    root.geometry("800x600")
    
    # Create test data with mixed types (including strings)
    test_data = pd.DataFrame({
        'symbol': ['COIN.US', 'AAPL.US', 'GOOGL.US', 'MSFT.US', 'TSLA.US'],
        'open': [100.0, 150.0, 200.0, 300.0, 400.0],
        'high': [110.0, 160.0, 210.0, 310.0, 410.0],
        'low': [90.0, 140.0, 190.0, 290.0, 390.0],
        'close': [105.0, 155.0, 205.0, 305.0, 405.0],
        'volume': [1000000, 2000000, 3000000, 4000000, 5000000]
    })
    
    print(f"✅ Created test data with shape: {test_data.shape}")
    print(f"✅ Data types: {test_data.dtypes.tolist()}")
    print(f"✅ Numeric columns: {test_data.select_dtypes(include=[np.number]).columns.tolist()}")
    
    # Test plot parameters
    plot_params = {
        'plot_type': '3D Scatter',
        'color_scheme': 'viridis',
        'point_size': 50
    }
    
    # Create a temporary model directory for testing
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    model_path = os.path.join(temp_dir, "test_model")
    os.makedirs(model_path, exist_ok=True)
    
    # Save test data to the model directory
    training_data_file = os.path.join(model_path, "training_data.csv")
    test_data.to_csv(training_data_file, index=False)
    print(f"✅ Saved test data to: {training_data_file}")
    
    try:
        # Import the floating 3D window
        from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
        
        # Create the floating 3D window
        print("🔄 Creating Floating3DWindow...")
        window = Floating3DWindow(root, model_path, plot_params)
        
        print("✅ Floating3DWindow created successfully")
        print("✅ Window should display 3D scatter plot using numeric columns only")
        print("✅ String columns (like 'symbol') should be ignored")
        print("✅ Plot should use: open, high, low columns for x, y, z")
        
        # Test different plot types
        plot_types = ["3D Scatter", "2D Scatter", "3D Surface", "3D Wireframe"]
        
        for plot_type in plot_types:
            print(f"\n🔄 Testing plot type: {plot_type}")
            plot_params['plot_type'] = plot_type
            window.plot_params = plot_params
            window.generate_plot_data()
            print(f"✅ {plot_type} plot generated successfully")
            time.sleep(1)  # Brief pause to see the plot
        
        print("\n✅ All plot types tested successfully")
        print("✅ No string-to-float conversion errors occurred")
        
        # Keep window open for manual inspection
        print("\n📋 Test completed successfully!")
        print("📋 Close the window to finish the test")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
    
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temporary directory: {e}")

if __name__ == "__main__":
    test_3d_plot_data_validation_fix() 