#!/usr/bin/env python3
"""
Test script for prediction integration with different model formats
"""

import os
import sys
import json
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_prediction_model_formats():
    """Test prediction integration with different model directory formats."""
    print("🧪 Testing prediction integration with different model formats...")
    
    try:
        from stock_prediction_gui.core.prediction_integration import PredictionIntegration
        
        # Create a mock app
        class MockApp:
            def __init__(self):
                self.data_manager = MockDataManager()
        
        class MockDataManager:
            def load_data(self, file_path):
                return {'success': True}
            
            def get_current_data(self):
                # Return mock data with required features
                import pandas as pd
                import numpy as np
                data = {
                    'open': np.random.rand(100) * 100 + 50,
                    'high': np.random.rand(100) * 100 + 50,
                    'low': np.random.rand(100) * 100 + 50,
                    'close': np.random.rand(100) * 100 + 50,
                    'vol': np.random.rand(100) * 1000000,
                    'ma_10': np.random.rand(100) * 100 + 50,
                    'rsi': np.random.rand(100) * 100,
                    'price_change': np.random.rand(100) * 10 - 5,
                    'volatility_10': np.random.rand(100) * 5
                }
                return pd.DataFrame(data)
        
        mock_app = MockApp()
        prediction_integration = PredictionIntegration(mock_app)
        
        # Test 1: Model with feature_info.json (new format)
        print("\n1️⃣ Testing model with feature_info.json...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create feature_info.json
            feature_info = {
                'x_features': ['open', 'high', 'low', 'close', 'vol'],
                'y_feature': 'close',
                'model_type': 'basic',
                'training_params': {'hidden_size': 4}
            }
            
            with open(os.path.join(temp_dir, 'feature_info.json'), 'w') as f:
                json.dump(feature_info, f)
            
            # Create mock model file
            with open(os.path.join(temp_dir, 'stock_model.npz'), 'w') as f:
                f.write('mock model data')
            
            # Create mock data file
            with open(os.path.join(temp_dir, 'test_data.csv'), 'w') as f:
                f.write('open,high,low,close,vol\n1,2,3,4,5')
            
            # Test parameter validation
            params = {
                'model_path': temp_dir,
                'data_file': os.path.join(temp_dir, 'test_data.csv')
            }
            
            if prediction_integration._validate_prediction_params(params):
                print("✅ feature_info.json format validation passed")
            else:
                print("❌ feature_info.json format validation failed")
                return False
        
        # Test 2: Model with model_params.json (old format)
        print("\n2️⃣ Testing model with model_params.json...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create model_params.json
            model_params = {
                'epochs': 100,
                'learning_rate': 0.001,
                'batch_size': 32,
                'hidden_size': 4,
                'validation_split': 0.2,
                'early_stopping_patience': 10,
                'random_seed': 42,
                'save_history': True,
                'memory_optimization': True
            }
            
            with open(os.path.join(temp_dir, 'model_params.json'), 'w') as f:
                json.dump(model_params, f)
            
            # Create mock model file
            with open(os.path.join(temp_dir, 'stock_model.npz'), 'w') as f:
                f.write('mock model data')
            
            # Create mock data file
            with open(os.path.join(temp_dir, 'test_data.csv'), 'w') as f:
                f.write('open,high,low,close,vol\n1,2,3,4,5')
            
            # Test parameter validation
            params = {
                'model_path': temp_dir,
                'data_file': os.path.join(temp_dir, 'test_data.csv')
            }
            
            if prediction_integration._validate_prediction_params(params):
                print("✅ model_params.json format validation passed")
            else:
                print("❌ model_params.json format validation failed")
                return False
        
        # Test 3: Model with no info files (fallback)
        print("\n3️⃣ Testing model with no info files (fallback)...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock model file only
            with open(os.path.join(temp_dir, 'stock_model.npz'), 'w') as f:
                f.write('mock model data')
            
            # Create mock data file
            with open(os.path.join(temp_dir, 'test_data.csv'), 'w') as f:
                f.write('open,high,low,close,vol\n1,2,3,4,5')
            
            # Test parameter validation
            params = {
                'model_path': temp_dir,
                'data_file': os.path.join(temp_dir, 'test_data.csv')
            }
            
            if prediction_integration._validate_prediction_params(params):
                print("✅ No info files fallback validation passed")
            else:
                print("❌ No info files fallback validation failed")
                return False
        
        # Test 4: Model with weights in weights_history directory
        print("\n4️⃣ Testing model with weights in weights_history...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create feature_info.json
            feature_info = {
                'x_features': ['open', 'high', 'low', 'close', 'vol'],
                'y_feature': 'close',
                'model_type': 'basic',
                'training_params': {'hidden_size': 4}
            }
            
            with open(os.path.join(temp_dir, 'feature_info.json'), 'w') as f:
                json.dump(feature_info, f)
            
            # Create weights_history directory with model files
            weights_dir = os.path.join(temp_dir, 'weights_history')
            os.makedirs(weights_dir, exist_ok=True)
            
            # Create mock weight files
            for i in range(3):
                with open(os.path.join(weights_dir, f'weights_history_{i:04d}.npz'), 'w') as f:
                    f.write(f'mock weight data {i}')
            
            # Create mock data file
            with open(os.path.join(temp_dir, 'test_data.csv'), 'w') as f:
                f.write('open,high,low,close,vol\n1,2,3,4,5')
            
            # Test parameter validation
            params = {
                'model_path': temp_dir,
                'data_file': os.path.join(temp_dir, 'test_data.csv')
            }
            
            if prediction_integration._validate_prediction_params(params):
                print("✅ Weights in weights_history validation passed")
            else:
                print("❌ Weights in weights_history validation failed")
                return False
        
        # Test 5: Invalid model directory
        print("\n5️⃣ Testing invalid model directory...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory with no model files
            params = {
                'model_path': temp_dir,
                'data_file': 'test_data.csv'
            }
            
            if not prediction_integration._validate_prediction_params(params):
                print("✅ Invalid model directory correctly rejected")
            else:
                print("❌ Invalid model directory should have been rejected")
                return False
        
        print("\n✅ All prediction model format tests passed!")
        print("\n📝 Summary:")
        print("   - feature_info.json format: ✅ Supported")
        print("   - model_params.json format: ✅ Supported")
        print("   - No info files fallback: ✅ Supported")
        print("   - Weights in weights_history: ✅ Supported")
        print("   - Invalid model directories: ✅ Properly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in prediction model format test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prediction_model_formats()
    if success:
        print("\n🎉 Prediction model format tests completed!")
    else:
        print("\n💥 Prediction model format tests failed!") 