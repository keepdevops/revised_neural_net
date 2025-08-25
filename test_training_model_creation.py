#!/usr/bin/env python3
"""
Test script to verify that the training system creates proper model directories
with timestamps and .npz files.
"""

import os
import sys
import tempfile
import shutil
import time
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_sample_data():
    """Create a sample CSV data file for testing."""
    import pandas as pd
    import numpy as np
    
    # Create sample stock data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = {
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 102 + np.random.randn(100).cumsum(),
        'vol': 1000000 + np.random.randint(-100000, 100000, 100)
    }
    
    df = pd.DataFrame(data)
    return df

def test_training_integration():
    """Test the training integration directly."""
    print("🧪 Testing Training Integration...")
    
    try:
        from stock_prediction_gui.core.training_integration import TrainingIntegration
        
        # Create a mock app object
        class MockApp:
            def __init__(self):
                self.current_output_dir = tempfile.mkdtemp()
        
        app = MockApp()
        integration = TrainingIntegration(app)
        
        # Create sample data
        df = create_sample_data()
        data_file = os.path.join(app.current_output_dir, 'sample_data.csv')
        df.to_csv(data_file, index=False)
        
        # Test parameters
        params = {
            'data_file': data_file,
            'x_features': ['open', 'high', 'low', 'vol'],
            'y_feature': 'close',
            'model_type': 'basic',
            'epochs': 10,  # Short for testing
            'learning_rate': 0.001,
            'batch_size': 32,
            'hidden_size': 4,
            'validation_split': 0.2,
            'early_stopping_patience': 5,
            'patience': 5,
            'history_interval': 5,
            'random_seed': 42,
            'save_history': True,
            'memory_optimization': False
        }
        
        # Test model directory creation
        model_dir = integration._create_model_directory()
        print(f"✅ Model directory created: {model_dir}")
        
        # Check if directory has timestamp format
        dir_name = os.path.basename(model_dir)
        if dir_name.startswith('model_') and len(dir_name) == 19:  # model_YYYYMMDD_HHMMSS
            print(f"✅ Directory has proper timestamp format: {dir_name}")
        else:
            print(f"❌ Directory format incorrect: {dir_name}")
            return False
        
        # Test training worker (this will create the actual model files)
        def progress_callback(epoch, loss, val_loss, progress):
            print(f"   Progress: Epoch {epoch}, Loss: {loss:.6f}, Val Loss: {val_loss:.6f}")
        
        def completion_callback(model_dir, error=None):
            if error:
                print(f"❌ Training failed: {error}")
            else:
                print(f"✅ Training completed: {model_dir}")
        
        # Start training
        success = integration.start_training(params, progress_callback, completion_callback)
        
        if success:
            print("✅ Training started successfully")
            
            # Wait for training to complete
            import time
            time.sleep(15)  # Give time for training to complete
            
            # Check for model files
            model_dirs = [d for d in os.listdir(app.current_output_dir) 
                         if d.startswith('model_')]
            
            if model_dirs:
                latest_model = max(model_dirs, key=lambda x: os.path.getctime(
                    os.path.join(app.current_output_dir, x)))
                model_path = os.path.join(app.current_output_dir, latest_model)
                
                print(f"✅ Found model directory: {model_path}")
                
                # Check for required files
                required_files = ['feature_info.json', 'training_losses.csv']
                for file in required_files:
                    file_path = os.path.join(model_path, file)
                    if os.path.exists(file_path):
                        print(f"✅ Found {file}")
                    else:
                        print(f"❌ Missing {file}")
                
                # Check for .npz file
                npz_files = [f for f in os.listdir(model_path) if f.endswith('.npz')]
                if npz_files:
                    print(f"✅ Found .npz files: {npz_files}")
                else:
                    print("❌ No .npz files found")
                
                # Check for weights_history directory
                weights_dir = os.path.join(model_path, 'weights_history')
                if os.path.exists(weights_dir):
                    weight_files = os.listdir(weights_dir)
                    print(f"✅ Found weights_history with {len(weight_files)} files")
                else:
                    print("❌ No weights_history directory")
                
                return True
            else:
                print("❌ No model directories created")
                return False
        else:
            print("❌ Training failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Training integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_script_launcher():
    """Test the script launcher approach."""
    print("\n🧪 Testing Script Launcher...")
    
    try:
        from script_launcher import launch_training
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Create sample data
        df = create_sample_data()
        data_file = os.path.join(temp_dir, 'sample_data.csv')
        df.to_csv(data_file, index=False)
        
        # Start training process
        process = launch_training(
            data_file=data_file,
            x_features=['open', 'high', 'low', 'vol'],
            y_feature='close',
            hidden_size=4,
            learning_rate=0.001,
            batch_size=32
        )
        
        print("✅ Training process started")
        
        # Wait for process to complete
        import time
        time.sleep(10)  # Give time for training
        
        # Check if process completed
        if process.poll() is not None:
            print("✅ Training process completed")
            
            # Check for model directories
            model_dirs = [d for d in os.listdir(temp_dir) if d.startswith('model_')]
            if model_dirs:
                latest_model = max(model_dirs, key=lambda x: os.path.getctime(
                    os.path.join(temp_dir, x)))
                model_path = os.path.join(temp_dir, latest_model)
                
                print(f"✅ Found model directory: {model_path}")
                
                # Check for .npz file
                npz_files = [f for f in os.listdir(model_path) if f.endswith('.npz')]
                if npz_files:
                    print(f"✅ Found .npz files: {npz_files}")
                    return True
                else:
                    print("❌ No .npz files found")
                    return False
            else:
                print("❌ No model directories created")
                return False
        else:
            print("❌ Training process did not complete")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Script launcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_training_manager():
    """Test the training manager."""
    print("\n🧪 Testing Training Manager...")
    
    try:
        from gui.training.training_manager import TrainingManager
        
        # Create a mock parent GUI
        class MockParentGUI:
            def __init__(self):
                pass
        
        parent_gui = MockParentGUI()
        manager = TrainingManager(parent_gui)
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Create sample data
        df = create_sample_data()
        data_file = os.path.join(temp_dir, 'sample_data.csv')
        df.to_csv(data_file, index=False)
        
        # Test parameters
        params = {
            'data_file': data_file,
            'output_dir': temp_dir,
            'x_features': ['open', 'high', 'low', 'vol'],
            'y_feature': 'close',
            'epochs': 5,  # Short for testing
            'learning_rate': 0.001,
            'batch_size': 32,
            'hidden_size': 4,
            'validation_split': 0.2,
            'early_stopping_patience': 3,
            'history_save_interval': 2,
            'random_seed': 42,
            'save_history': True,
            'memory_optimization': False
        }
        
        # Test callback
        def callback(status, data):
            if status == 'completed':
                print(f"✅ Training completed: {data}")
            elif status == 'error':
                print(f"❌ Training error: {data}")
            else:
                epoch, loss, val_loss, progress = data
                print(f"   Progress: Epoch {epoch}, Loss: {loss:.6f}, Progress: {progress:.1f}%")
        
        # Start training
        success = manager.start_training(params, callback)
        
        if success:
            print("✅ Training manager started successfully")
            
            # Wait for training to complete
            import time
            time.sleep(10)  # Give time for training
            
            # Check for model directories
            model_dirs = [d for d in os.listdir(temp_dir) if d.startswith('model_')]
            if model_dirs:
                latest_model = max(model_dirs, key=lambda x: os.path.getctime(
                    os.path.join(temp_dir, x)))
                model_path = os.path.join(temp_dir, latest_model)
                
                print(f"✅ Found model directory: {model_path}")
                
                # Check for .npz file
                npz_files = [f for f in os.listdir(model_path) if f.endswith('.npz')]
                if npz_files:
                    print(f"✅ Found .npz files: {npz_files}")
                    return True
                else:
                    print("❌ No .npz files found")
                    return False
            else:
                print("❌ No model directories created")
                return False
        else:
            print("❌ Training manager failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Training manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Training Model Creation System")
    print("=" * 50)
    
    results = []
    
    # Test 1: Training Integration
    print("\n1. Testing Training Integration...")
    result1 = test_training_integration()
    results.append(("Training Integration", result1))
    
    # Test 2: Script Launcher
    print("\n2. Testing Script Launcher...")
    result2 = test_script_launcher()
    results.append(("Script Launcher", result2))
    
    # Test 3: Training Manager
    print("\n3. Testing Training Manager...")
    result3 = test_training_manager()
    results.append(("Training Manager", result3))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Training system creates proper model directories with .npz files.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 