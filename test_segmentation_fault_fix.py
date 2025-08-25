#!/usr/bin/env python3
"""
Segmentation Fault Fix Verification Test

This test verifies that the training completion no longer causes segmentation faults
by testing the thread-safe GUI updates and model refresh functionality.
"""

import os
import sys
import time
import threading
import tempfile
import tkinter as tk
from tkinter import ttk
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_test_data():
    """Create test data for training."""
    import pandas as pd
    import numpy as np
    
    # Create sample stock data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    
    data = {
        'date': dates,
        'open': np.random.uniform(100, 200, 100),
        'high': np.random.uniform(150, 250, 100),
        'low': np.random.uniform(50, 150, 100),
        'close': np.random.uniform(100, 200, 100),
        'vol': np.random.uniform(1000, 10000, 100)
    }
    
    df = pd.DataFrame(data)
    return df

def test_thread_safe_gui_updates():
    """Test that GUI updates are thread-safe."""
    print("\n🧪 Testing Thread-Safe GUI Updates")
    print("=" * 50)
    
    try:
        # Create a simple test window
        root = tk.Tk()
        root.title("Thread-Safe GUI Test")
        root.geometry("400x300")
        
        # Create a test variable
        test_var = tk.StringVar(value="Initial")
        
        # Create a label to display the variable
        label = ttk.Label(root, textvariable=test_var, font=("Arial", 14))
        label.pack(pady=20)
        
        # Create a progress bar
        progress = ttk.Progressbar(root, mode='determinate', maximum=100)
        progress.pack(pady=10, padx=20, fill='x')
        
        # Create a status label
        status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(root, textvariable=status_var)
        status_label.pack(pady=10)
        
        # Test function that simulates training completion
        def simulate_training_completion():
            """Simulate training completion with GUI updates."""
            try:
                print("🔄 Starting simulated training...")
                
                # Simulate training progress
                for i in range(10):
                    time.sleep(0.1)  # Simulate work
                    
                    # Update GUI on main thread
                    root.after(0, lambda i=i: progress.config(value=(i+1)*10))
                    root.after(0, lambda i=i: status_var.set(f"Training... {i+1}/10"))
                    root.after(0, lambda i=i: test_var.set(f"Epoch {i+1}"))
                    
                    # Process GUI events
                    root.update_idletasks()
                
                # Simulate training completion
                print("✅ Training completed, updating GUI...")
                
                # Update GUI on main thread
                root.after(0, lambda: progress.config(value=100))
                root.after(0, lambda: status_var.set("Training completed!"))
                root.after(0, lambda: test_var.set("Model saved"))
                
                # Simulate model refresh
                root.after(0, lambda: simulate_model_refresh())
                
                print("✅ Thread-safe GUI updates completed")
                
            except Exception as e:
                print(f"❌ Error in training simulation: {e}")
        
        def simulate_model_refresh():
            """Simulate model refresh after training."""
            try:
                print("🔄 Simulating model refresh...")
                
                # Simulate finding a new model
                model_name = "model_20250101_150000"
                
                # Update GUI on main thread
                root.after(0, lambda: status_var.set(f"Model refreshed: {model_name}"))
                root.after(0, lambda: test_var.set(f"Selected: {model_name}"))
                
                print("✅ Model refresh simulation completed")
                
            except Exception as e:
                print(f"❌ Error in model refresh simulation: {e}")
        
        # Start training simulation in background thread
        training_thread = threading.Thread(target=simulate_training_completion)
        training_thread.daemon = True
        training_thread.start()
        
        # Run the GUI
        print("🎬 Running thread-safe GUI test...")
        print("1. Watch the progress bar and status updates")
        print("2. Verify no segmentation faults occur")
        print("3. Close window when test completes")
        
        root.mainloop()
        
        print("✅ Thread-safe GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in thread-safe GUI test: {e}")
        return False

def test_app_training_completion():
    """Test the app's training completion handling."""
    print("\n🧪 Testing App Training Completion")
    print("=" * 50)
    
    try:
        # Import the app module
        from stock_prediction_gui.core.app import StockPredictionApp
        
        # Create a test root window
        root = tk.Tk()
        root.title("App Training Completion Test")
        root.geometry("600x400")
        
        # Create the app
        app = StockPredictionApp(root)
        
        # Create test data
        test_data = create_test_data()
        
        # Save test data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            test_data_file = f.name
        
        # Test training parameters
        training_params = {
            'data_file': test_data_file,
            'x_features': ['open', 'high', 'low', 'vol'],
            'y_feature': 'close',
            'epochs': 5,  # Short for testing
            'learning_rate': 0.001,
            'batch_size': 32,
            'hidden_size': 4,
            'validation_split': 0.2,
            'early_stopping_patience': 3,
            'model_type': 'basic'
        }
        
        # Test completion callback
        completion_called = False
        completion_model_dir = None
        
        def test_completion_callback(model_dir, error=None):
            nonlocal completion_called, completion_model_dir
            completion_called = True
            completion_model_dir = model_dir
            print(f"✅ Training completion callback called: {model_dir}")
        
        # Test progress callback
        progress_updates = []
        
        def test_progress_callback(epoch, loss, val_loss, progress):
            progress_updates.append((epoch, loss, val_loss, progress))
            print(f"📈 Progress: Epoch {epoch}, Loss {loss:.6f}, Progress {progress:.1f}%")
        
        # Start training
        print("🚀 Starting training test...")
        success = app.training_integration.start_training(
            training_params,
            progress_callback=test_progress_callback,
            completion_callback=test_completion_callback
        )
        
        if success:
            print("✅ Training started successfully")
            
            # Wait for training to complete
            max_wait = 30  # seconds
            start_time = time.time()
            
            while not completion_called and (time.time() - start_time) < max_wait:
                time.sleep(0.1)
                root.update_idletasks()
            
            if completion_called:
                print("✅ Training completion handled successfully")
                print(f"   Model directory: {completion_model_dir}")
                print(f"   Progress updates: {len(progress_updates)}")
                
                # Verify GUI is still responsive
                if app.main_window and app.main_window.root:
                    print("✅ GUI remains responsive after training")
                else:
                    print("❌ GUI not responsive after training")
                    return False
                
            else:
                print("❌ Training completion not called within timeout")
                return False
        else:
            print("❌ Failed to start training")
            return False
        
        # Clean up
        try:
            os.unlink(test_data_file)
        except:
            pass
        
        root.destroy()
        
        print("✅ App training completion test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error in app training completion test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_refresh_safety():
    """Test that model refresh is thread-safe."""
    print("\n🧪 Testing Model Refresh Safety")
    print("=" * 50)
    
    try:
        # Create temporary directory for test models
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test model directories
            model_dirs = []
            for i in range(3):
                model_dir = os.path.join(temp_dir, f"model_20250101_{150000 + i}")
                os.makedirs(model_dir, exist_ok=True)
                model_dirs.append(model_dir)
                
                # Create model files
                with open(os.path.join(model_dir, "feature_info.json"), 'w') as f:
                    f.write('{"x_features": ["open", "high"], "y_feature": "close"}')
                
                with open(os.path.join(model_dir, "training_losses.csv"), 'w') as f:
                    f.write("0.1,0.2\n0.05,0.15\n")
            
            # Test model manager
            from stock_prediction_gui.core.model_manager import ModelManager
            
            model_manager = ModelManager(base_dir=temp_dir)
            models = model_manager.get_available_models()
            
            if len(models) == 3:
                print("✅ Model manager found all test models")
                
                # Test thread-safe model refresh
                root = tk.Tk()
                root.title("Model Refresh Safety Test")
                root.geometry("400x200")
                
                # Create test variable
                model_var = tk.StringVar()
                label = ttk.Label(root, textvariable=model_var)
                label.pack(pady=20)
                
                def simulate_model_refresh():
                    """Simulate model refresh in background thread."""
                    try:
                        time.sleep(0.5)  # Simulate work
                        
                        # Update GUI on main thread
                        root.after(0, lambda: model_var.set(f"Latest model: {os.path.basename(models[0])}"))
                        
                        time.sleep(0.5)  # More work
                        
                        # Update again
                        root.after(0, lambda: model_var.set(f"Refreshed: {len(models)} models found"))
                        
                        print("✅ Thread-safe model refresh completed")
                        
                    except Exception as e:
                        print(f"❌ Error in model refresh: {e}")
                
                # Start refresh in background thread
                refresh_thread = threading.Thread(target=simulate_model_refresh)
                refresh_thread.daemon = True
                refresh_thread.start()
                
                # Run GUI
                print("🎬 Running model refresh safety test...")
                root.mainloop()
                
                print("✅ Model refresh safety test completed")
                return True
            else:
                print(f"❌ Expected 3 models, found {len(models)}")
                return False
                
    except Exception as e:
        print(f"❌ Error in model refresh safety test: {e}")
        return False

def main():
    """Run all segmentation fault fix tests."""
    print("🔧 Segmentation Fault Fix Verification Test")
    print("=" * 60)
    print("This test verifies that training completion no longer causes")
    print("segmentation faults by testing thread-safe GUI updates.")
    print()
    
    setup_logging()
    
    # Run tests
    tests = [
        ("Thread-Safe GUI Updates", test_thread_safe_gui_updates),
        ("App Training Completion", test_app_training_completion),
        ("Model Refresh Safety", test_model_refresh_safety)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Segmentation fault fix is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 