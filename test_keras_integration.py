"""
Test script for Keras model integration.

This script tests the Keras model integration with the stock prediction system.
"""

import os
import sys
import numpy as np
import pandas as pd
import tempfile
import shutil
from datetime import datetime

def test_keras_availability():
    """Test if Keras is available."""
    try:
        from keras_model_integration import KerasModelIntegration, KERAS_AVAILABLE
        print(f"✅ Keras integration available: {KERAS_AVAILABLE}")
        return KERAS_AVAILABLE
    except ImportError as e:
        print(f"❌ Keras integration not available: {e}")
        return False

def test_keras_training():
    """Test Keras model training."""
    if not test_keras_availability():
        print("⚠️ Skipping Keras training test - Keras not available")
        return False
    
    try:
        from keras_model_integration import KerasModelIntegration
        
        # Create test data
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples, 1)
        
        # Create integration instance
        integration = KerasModelIntegration()
        
        # Train model
        print("Training Keras model...")
        model, history = integration.train_model(
            X, y,
            model_params={
                'hidden_sizes': [32, 16],
                'epochs': 5,  # Short training for test
                'batch_size': 16
            }
        )
        
        print(f"✅ Keras training test passed!")
        print(f"Model trained for {len(history.history['loss'])} epochs")
        print(f"Final loss: {history.history['loss'][-1]:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Keras training test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keras_save_load():
    """Test Keras model saving and loading."""
    if not test_keras_availability():
        print("⚠️ Skipping Keras save/load test - Keras not available")
        return False
    
    try:
        from keras_model_integration import KerasModelIntegration
        
        # Create test data
        np.random.seed(42)
        X = np.random.randn(50, 4)
        y = np.random.randn(50, 1)
        
        # Create integration instance
        integration = KerasModelIntegration()
        
        # Train model
        model, history = integration.train_model(
            X, y,
            model_params={
                'hidden_sizes': [16],
                'epochs': 3,
                'batch_size': 16
            }
        )
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save model
            feature_info = {
                'x_features': ['feature_1', 'feature_2', 'feature_3', 'feature_4'],
                'y_feature': 'target',
                'model_type': 'keras'
            }
            
            model_path = integration.save_model(model, temp_dir, feature_info)
            print(f"✅ Model saved to: {model_path}")
            
            # Load model
            loaded_model, loaded_feature_info = integration.load_model(temp_dir)
            print(f"✅ Model loaded successfully")
            
            # Make predictions
            predictions = integration.predict(loaded_model, X, loaded_feature_info)
            print(f"✅ Predictions made: {predictions.shape}")
            
            # Verify predictions are reasonable
            assert len(predictions) == len(X), "Prediction length mismatch"
            assert not np.any(np.isnan(predictions)), "Predictions contain NaN values"
            
            print(f"✅ Keras save/load test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Keras save/load test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keras_with_training_integration():
    """Test Keras integration with the training system."""
    if not test_keras_availability():
        print("⚠️ Skipping training integration test - Keras not available")
        return False
    
    try:
        # Create test data file
        np.random.seed(42)
        n_samples = 100
        data = {
            'open': np.random.randn(n_samples),
            'high': np.random.randn(n_samples),
            'low': np.random.randn(n_samples),
            'close': np.random.randn(n_samples),
            'vol': np.random.randn(n_samples)
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            data_file = f.name
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as output_dir:
            # Test training integration
            from stock_prediction_gui.core.training_integration import TrainingIntegration
            
            # Mock app object
            class MockApp:
                def __init__(self):
                    self.current_output_dir = output_dir
                    self.data_manager = MockDataManager()
            
            class MockDataManager:
                def load_data(self, file_path):
                    return True
                
                def get_current_data(self):
                    return df
            
            app = MockApp()
            training_integration = TrainingIntegration(app)
            
            # Training parameters
            params = {
                'data_file': data_file,
                'x_features': ['open', 'high', 'low', 'vol'],
                'y_feature': 'close',
                'model_type': 'keras',
                'epochs': 3,
                'batch_size': 16,
                'hidden_sizes': [16],
                'dropout_rate': 0.1
            }
            
            # Mock callbacks
            def progress_callback(epoch, loss, val_loss, progress):
                print(f"Training progress: Epoch {epoch}, Loss: {loss:.6f}")
            
            def completion_callback(result):
                if result:
                    print(f"✅ Training completed: {result}")
                else:
                    print("❌ Training failed")
            
            # Start training
            success = training_integration.start_training(params, progress_callback, completion_callback)
            
            if success:
                # Wait for training to complete
                import time
                time.sleep(10)  # Give some time for training
                
                # Check if model directory was created
                model_dirs = [d for d in os.listdir(output_dir) if d.startswith('model_')]
                if model_dirs:
                    model_dir = os.path.join(output_dir, model_dirs[0])
                    print(f"✅ Model directory created: {model_dir}")
                    
                    # Check for Keras model file (both .keras and .h5 formats)
                    model_file_keras = os.path.join(model_dir, 'model.keras')
                    model_file_h5 = os.path.join(model_dir, 'model.h5')
                    
                    if os.path.exists(model_file_keras):
                        print(f"✅ Keras model file created: {model_file_keras}")
                        return True
                    elif os.path.exists(model_file_h5):
                        print(f"✅ Keras model file created: {model_file_h5}")
                        return True
                    else:
                        print(f"❌ Keras model file not found")
                        return False
                else:
                    print("❌ No model directory created")
                    return False
            else:
                print("❌ Training failed to start")
                return False
                
    except Exception as e:
        print(f"❌ Training integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if 'data_file' in locals():
            try:
                os.unlink(data_file)
            except:
                pass

def test_keras_with_prediction_integration():
    """Test Keras integration with the prediction system."""
    if not test_keras_availability():
        print("⚠️ Skipping prediction integration test - Keras not available")
        return False
    
    try:
        from keras_model_integration import KerasModelIntegration
        
        # Create test data
        np.random.seed(42)
        X = np.random.randn(20, 4)
        y = np.random.randn(20, 1)
        
        # Train and save a Keras model
        integration = KerasModelIntegration()
        model, history = integration.train_model(
            X, y,
            model_params={
                'hidden_sizes': [16],
                'epochs': 3,
                'batch_size': 16
            }
        )
        
        with tempfile.TemporaryDirectory() as model_dir:
            # Save model
            feature_info = {
                'x_features': ['feature_1', 'feature_2', 'feature_3', 'feature_4'],
                'y_feature': 'target',
                'model_type': 'keras'
            }
            integration.save_model(model, model_dir, feature_info)
            
            # Create test data file
            test_data = pd.DataFrame(X, columns=feature_info['x_features'])
            test_data[feature_info['y_feature']] = y.flatten()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                test_data.to_csv(f.name, index=False)
                data_file = f.name
            
            # Test prediction integration
            from stock_prediction_gui.core.prediction_integration import PredictionIntegration
            
            # Mock app object
            class MockApp:
                def __init__(self):
                    self.data_manager = MockDataManager()
            
            class MockDataManager:
                def load_data(self, file_path):
                    return True
                
                def get_current_data(self):
                    return test_data
            
            app = MockApp()
            prediction_integration = PredictionIntegration(app)
            
            # Prediction parameters
            params = {
                'data_file': data_file,
                'model_path': model_dir
            }
            
            # Mock callbacks with proper signature
            def completion_callback(result, error=None):
                if error:
                    print(f"❌ Prediction failed: {error}")
                elif result:
                    print(f"✅ Prediction completed: {result}")
                else:
                    print("❌ Prediction failed")
            
            # Start prediction
            success = prediction_integration.start_prediction(params, completion_callback=completion_callback)
            
            if success:
                # Wait for prediction to complete
                import time
                time.sleep(5)  # Give some time for prediction
                
                # Check if prediction file was created
                prediction_files = [f for f in os.listdir(model_dir) if f.startswith('predictions_')]
                if prediction_files:
                    print(f"✅ Prediction file created: {prediction_files[0]}")
                    return True
                else:
                    print("❌ No prediction file created")
                    return False
            else:
                print("❌ Prediction failed to start")
                return False
                
    except Exception as e:
        print(f"❌ Prediction integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if 'data_file' in locals():
            try:
                os.unlink(data_file)
            except:
                pass

def main():
    """Run all Keras integration tests."""
    print("🧪 Testing Keras Model Integration")
    print("=" * 50)
    
    tests = [
        ("Keras Availability", test_keras_availability),
        ("Keras Training", test_keras_training),
        ("Keras Save/Load", test_keras_save_load),
        ("Training Integration", test_keras_with_training_integration),
        ("Prediction Integration", test_keras_with_prediction_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"{test_name}: ❌ FAIL - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Keras integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main() 