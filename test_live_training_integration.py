#!/usr/bin/env python3
"""
Test script to verify live training integration with plot updates.
"""

import os
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_live_training_integration():
    """Test the complete live training integration."""
    print("🧪 Testing Live Training Integration")
    print("=" * 50)
    
    # Create a temporary data file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("open,high,low,close,vol\n")
        for i in range(100):
            f.write(f"{100+i},{101+i},{99+i},{100.5+i},{1000+i}\n")
        temp_data_file = f.name
    
    print(f"📁 Created test data file: {temp_data_file}")
    
    # Create temporary output directory
    temp_output_dir = tempfile.mkdtemp()
    print(f"📁 Created output directory: {temp_output_dir}")
    
    # Test parameters
    test_params = {
        'data_file': temp_data_file,
        'output_dir': temp_output_dir,
        'x_features': ['open', 'high', 'low', 'vol'],
        'y_feature': 'close',
        'epochs': 5,  # Short test
        'learning_rate': 0.001,
        'batch_size': 32,
        'hidden_size': 4,
        'validation_split': 0.2,
        'early_stopping_patience': 10,
        'history_save_interval': 10,
        'random_seed': 42,
        'save_history': True,
        'memory_optimization': False,
        'model_type': 'basic'
    }
    
    # Test callback function
    progress_updates = []
    
    def test_callback(status, data):
        if status == 'progress':
            epoch, loss, val_loss, percent = data
            progress_updates.append((epoch, loss, val_loss, percent))
            print(f"📈 Progress: Epoch {epoch}, Loss {loss:.6f}, Progress {percent:.1f}%")
        elif status == 'completed':
            print(f"✅ Training completed: {data}")
        elif status == 'error':
            print(f"❌ Training error: {data}")
    
    try:
        # Import and test training manager
        from gui.training.training_manager import TrainingManager
        
        # Create a mock parent GUI
        class MockParentGUI:
            def __init__(self):
                self.logger = None
        
        # Create training manager
        training_manager = TrainingManager(MockParentGUI())
        
        print("🎬 Starting training with live updates...")
        
        # Start training
        success = training_manager.start_training(test_params, test_callback)
        
        if success:
            print("✅ Training started successfully")
            
            # Wait for training to complete (with timeout)
            timeout = 30  # seconds
            start_time = time.time()
            
            while training_manager.is_training and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            if training_manager.is_training:
                print("⏰ Training timed out")
                training_manager.stop_training()
            else:
                print("✅ Training completed")
            
            # Check results
            print(f"\n📊 Training Results:")
            print(f"Progress updates received: {len(progress_updates)}")
            
            if progress_updates:
                print("✅ SUCCESS: Live plot updates are working!")
                print("📈 Progress data:")
                for epoch, loss, val_loss, percent in progress_updates:
                    print(f"  Epoch {epoch}: Loss {loss:.6f}, Progress {percent:.1f}%")
                
                # Check if loss is decreasing (good training)
                if len(progress_updates) > 1:
                    first_loss = progress_updates[0][1]
                    last_loss = progress_updates[-1][1]
                    if last_loss < first_loss:
                        print("✅ Loss is decreasing - training is working!")
                    else:
                        print("⚠️ Loss is not decreasing - check training parameters")
            else:
                print("❌ No progress updates received")
                
        else:
            print("❌ Failed to start training")
        
        # Check if model files were created
        model_dirs = [d for d in os.listdir(temp_output_dir) if d.startswith('model_')]
        if model_dirs:
            print(f"✅ Model directory created: {model_dirs[0]}")
            
            # Check for required files
            model_dir = os.path.join(temp_output_dir, model_dirs[0])
            required_files = ['stock_model.npz', 'feature_info.json', 'training_data.csv']
            for file in required_files:
                file_path = os.path.join(model_dir, file)
                if os.path.exists(file_path):
                    print(f"✅ {file} exists")
                else:
                    print(f"❌ {file} missing")
        else:
            print("❌ No model directory created")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            os.unlink(temp_data_file)
            import shutil
            shutil.rmtree(temp_output_dir)
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Live Training Integration Test Completed!")
    
    if len(progress_updates) > 0:
        print("✅ SUCCESS: Live training integration is working!")
        print("💡 The GUI should now show live plot updates during training.")
    else:
        print("❌ FAILED: No live updates received.")
        print("💡 Check the training manager and callback implementation.")

if __name__ == "__main__":
    test_live_training_integration() 