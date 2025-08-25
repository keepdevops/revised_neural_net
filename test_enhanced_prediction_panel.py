#!/usr/bin/env python3
"""
Test script for the enhanced prediction panel with forward pass visualization.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import threading
import time
import numpy as np

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_enhanced_prediction_panel():
    """Test the enhanced prediction panel with forward pass visualization."""
    print("🧪 Testing Enhanced Prediction Panel with Forward Pass Visualization")
    print("=" * 70)
    
    # Create test window
    root = tk.Tk()
    root.title("Enhanced Prediction Panel Test")
    root.geometry("1200x800")
    
    # Mock app object
    class MockApp:
        def __init__(self):
            self.selected_model = None
            self.current_data_file = None
            self.prediction_batch_size = 32
            self.prediction_confidence = 0.8
            
            # Mock data manager
            self.data_manager = MockDataManager()
            
            # Mock model manager
            self.model_manager = MockModelManager()
            
        def refresh_models(self):
            print("🔄 Refreshing models...")
            
        def refresh_models_and_select_latest(self):
            print("🔄 Refreshing and selecting latest model...")
            self.selected_model = "/path/to/latest/model"
            
        def start_prediction(self, params, callback=None):
            print(f"🚀 Starting prediction with params: {params}")
            
            # Simulate prediction process with forward pass data
            def simulate_prediction():
                total_steps = 50
                for step in range(total_steps):
                    if step % 5 == 0:  # Update every 5 steps
                        # Simulate weights and bias
                        weights = np.random.randn(4) * 0.1
                        bias = np.random.randn() * 0.1
                        prediction = np.random.randn() * 0.5 + 100
                        input_data = np.random.randn(4) * 10 + 50
                        progress = (step / total_steps) * 100
                        
                        # Call the progress callback
                        if callback:
                            callback(weights, bias, prediction, input_data, progress)
                        
                        time.sleep(0.1)  # Simulate processing time
                
                # Call completion callback
                if callback:
                    callback(None, None, None, None, 100)  # Final progress
                    
            # Start simulation in background thread
            thread = threading.Thread(target=simulate_prediction, daemon=True)
            thread.start()
            return True
    
    class MockDataManager:
        def load_data(self, file_path):
            print(f"📊 Loading data from: {file_path}")
            return True
        
        def get_current_data(self):
            # Return mock data
            return np.random.randn(100, 5)
    
    class MockModelManager:
        def get_available_models(self):
            return [
                "/path/to/model_20250627_221417",
                "/path/to/model_20250627_220848",
                "/path/to/model_20250627_194656"
            ]
    
    # Create mock app
    app = MockApp()
    
    try:
        # Import the enhanced prediction panel
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        
        # Create the prediction panel
        print("📋 Creating enhanced prediction panel...")
        prediction_panel = PredictionPanel(root, app)
        prediction_panel.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        print("✅ Enhanced prediction panel created successfully!")
        print("\n🎯 Test Instructions:")
        print("1. The left panel shows condensed prediction controls")
        print("2. The right panel shows the forward pass visualizer")
        print("3. Click '🚀 Predict' to see live forward pass visualization")
        print("4. Toggle 'Live Animation' to see real-time updates")
        print("5. The visualizer shows weights, bias, and prediction evolution")
        
        # Add test controls
        test_frame = ttk.LabelFrame(root, text="Test Controls", padding="10")
        test_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def test_prediction():
            print("🧪 Starting test prediction...")
            prediction_panel.make_prediction()
        
        def test_clear():
            print("🧹 Clearing visualization...")
            prediction_panel.clear_results()
        
        def test_add_sample_data():
            print("📊 Adding sample forward pass data...")
            # Add some sample data to the visualizer
            for i in range(10):
                weights = np.random.randn(4) * 0.1
                bias = np.random.randn() * 0.1
                prediction = np.random.randn() * 0.5 + 100
                input_data = np.random.randn(4) * 10 + 50
                
                prediction_panel.forward_pass_visualizer.add_forward_pass_data(
                    weights, bias, prediction, input_data
                )
                time.sleep(0.1)
        
        # Test buttons
        btn_frame = ttk.Frame(test_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="🧪 Test Prediction", command=test_prediction).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="📊 Add Sample Data", command=test_add_sample_data).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Clear", command=test_clear).pack(side="left", padx=(0, 5))
        
        # Status label
        status_var = tk.StringVar(value="Ready for testing")
        ttk.Label(test_frame, textvariable=status_var, font=("Arial", 10, "bold")).pack(pady=(10, 0))
        
        print("\n🎮 Test window ready! Close the window to exit.")
        
        # Run the GUI
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Error creating prediction panel: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_forward_pass_visualizer():
    """Test the forward pass visualizer component independently."""
    print("\n🔬 Testing Forward Pass Visualizer Component")
    print("=" * 50)
    
    # Create test window
    root = tk.Tk()
    root.title("Forward Pass Visualizer Test")
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
        test_frame = ttk.LabelFrame(root, text="Visualizer Test Controls", padding="10")
        test_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def add_random_data():
            print("📊 Adding random forward pass data...")
            weights = np.random.randn(4) * 0.1
            bias = np.random.randn() * 0.1
            prediction = np.random.randn() * 0.5 + 100
            input_data = np.random.randn(4) * 10 + 50
            
            visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
        
        def add_sequence_data():
            print("📈 Adding sequence of forward pass data...")
            for i in range(20):
                weights = np.array([0.1 + i*0.01, 0.2 + i*0.005, 0.3 - i*0.002, 0.4 + i*0.003])
                bias = 0.5 + i*0.01
                prediction = 100 + i*0.5 + np.random.randn() * 0.1
                input_data = np.array([50 + i, 60 + i*0.8, 70 + i*0.6, 80 + i*0.4])
                
                visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
                time.sleep(0.05)
        
        def toggle_animation():
            print("🎬 Toggling live animation...")
            visualizer.animation_var.set(not visualizer.animation_var.get())
        
        def clear_visualization():
            print("🧹 Clearing visualization...")
            visualizer.clear_visualization()
        
        # Test buttons
        btn_frame = ttk.Frame(test_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="📊 Add Random Data", command=add_random_data).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="📈 Add Sequence", command=add_sequence_data).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="🎬 Toggle Animation", command=toggle_animation).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Clear", command=clear_visualization).pack(side="left", padx=(0, 5))
        
        print("\n🎮 Visualizer test window ready! Close the window to exit.")
        
        # Run the GUI
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating visualizer: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Enhanced Prediction Panel Test Suite")
    print("=" * 50)
    
    # Test the forward pass visualizer first
    if test_forward_pass_visualizer():
        print("\n✅ Forward pass visualizer test completed successfully!")
    else:
        print("\n❌ Forward pass visualizer test failed!")
    
    # Test the full prediction panel
    if test_enhanced_prediction_panel():
        print("\n✅ Enhanced prediction panel test completed successfully!")
    else:
        print("\n❌ Enhanced prediction panel test failed!")
    
    print("\n🎉 Test suite completed!") 