#!/usr/bin/env python3
"""
Test script to verify enhanced prediction functionality with model validation.
"""

import os
import sys
import tempfile
import json
import numpy as np
import pandas as pd

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_enhanced_prediction():
    """Test the enhanced prediction functionality."""
    print("🧪 Testing Enhanced Prediction Functionality")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.prediction_integration import PredictionIntegration
        
        # Create a mock app object
        class MockApp:
            def __init__(self):
                self.data_manager = None
        
        app = MockApp()
        prediction_integration = PredictionIntegration(app)
        
        # Test 1: Test model file validation
        print("\n1️⃣ Testing model file validation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an empty model directory (invalid)
            empty_model_dir = os.path.join(temp_dir, "empty_model")
            os.makedirs(empty_model_dir, exist_ok=True)
            
            # Test validation by checking if enhanced search returns None
            model_file = prediction_integration._find_model_file_enhanced(empty_model_dir)
            
            if model_file is None:
                print("✅ Model validation correctly identified empty directory as invalid")
            else:
                print("❌ Model validation incorrectly identified empty directory as valid")
                return False
            
            # Create a valid model directory
            valid_model_dir = os.path.join(temp_dir, "valid_model")
            os.makedirs(valid_model_dir, exist_ok=True)
            
            # Create a mock model file
            mock_weights = {
                'W1': np.random.randn(4, 8),
                'b1': np.random.randn(1, 8),
                'W2': np.random.randn(8, 1),
                'b2': np.random.randn(1, 1),
                'input_size': 4,
                'hidden_size': 8
            }
            np.savez(os.path.join(valid_model_dir, "stock_model.npz"), **mock_weights)
            
            # Test validation by checking if enhanced search finds the file
            model_file = prediction_integration._find_model_file_enhanced(valid_model_dir)
            
            if model_file and "stock_model.npz" in model_file:
                print("✅ Model validation correctly identified valid model directory")
            else:
                print("❌ Model validation incorrectly identified valid model directory as invalid")
                return False
        
        # Test 2: Test enhanced model file search
        print("\n2️⃣ Testing enhanced model file search...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a model directory structure
            stock_prediction_gui_dir = os.path.join(temp_dir, "stock_prediction_gui")
            os.makedirs(stock_prediction_gui_dir, exist_ok=True)
            
            # Create an empty model directory
            empty_model_dir = os.path.join(stock_prediction_gui_dir, "model_20250626_232921")
            os.makedirs(empty_model_dir, exist_ok=True)
            
            # Create a working model directory in the parent
            working_model_dir = os.path.join(temp_dir, "model_20250627_161316")
            os.makedirs(working_model_dir, exist_ok=True)
            
            # Create a mock model file
            mock_weights = {
                'W1': np.random.randn(4, 8),
                'b1': np.random.randn(1, 8),
                'W2': np.random.randn(8, 1),
                'b2': np.random.randn(1, 1),
                'input_size': 4,
                'hidden_size': 8
            }
            np.savez(os.path.join(working_model_dir, "stock_model.npz"), **mock_weights)
            
            # Test the enhanced search
            model_file = prediction_integration._find_model_file_enhanced(empty_model_dir)
            
            if model_file and "stock_model.npz" in model_file:
                print("✅ Enhanced search found model file in parent directory")
                print(f"Found: {model_file}")
            else:
                print("❌ Enhanced search failed to find model file in parent directory")
                return False
        
        # Test 3: Test error message generation
        print("\n3️⃣ Testing error message generation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a model directory with some files but no model files
            model_dir = os.path.join(temp_dir, "model_20250626_232921")
            os.makedirs(model_dir, exist_ok=True)
            
            # Create some non-model files
            with open(os.path.join(model_dir, "model_params.json"), 'w') as f:
                json.dump({"epochs": 100}, f)
            
            os.makedirs(os.path.join(model_dir, "plots"), exist_ok=True)
            os.makedirs(os.path.join(model_dir, "weights_history"), exist_ok=True)
            
            # Test error message generation
            error_msg = prediction_integration._generate_model_not_found_error(model_dir)
            
            if "No model file found" in error_msg and "model_params.json" in error_msg:
                print("✅ Error message generation works correctly")
                print(f"Error message preview: {error_msg[:200]}...")
            else:
                print("❌ Error message generation failed")
                print(f"Generated message: {error_msg}")
                return False
        
        # Test 4: Test with actual prediction scenario
        print("\n4️⃣ Testing prediction scenario with missing model files...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = pd.DataFrame({
                'open': np.random.randn(100) * 10 + 100,
                'high': np.random.randn(100) * 10 + 105,
                'low': np.random.randn(100) * 10 + 95,
                'close': np.random.randn(100) * 10 + 100,
                'vol': np.random.randint(1000, 10000, 100)
            })
            
            data_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(data_file, index=False)
            
            # Create an empty model directory
            empty_model_dir = os.path.join(temp_dir, "model_20250626_232921")
            os.makedirs(empty_model_dir, exist_ok=True)
            
            # Create a working model directory
            working_model_dir = os.path.join(temp_dir, "model_20250627_161316")
            os.makedirs(working_model_dir, exist_ok=True)
            
            # Create a mock model file
            mock_weights = {
                'W1': np.random.randn(4, 8),
                'b1': np.random.randn(1, 8),
                'W2': np.random.randn(8, 1),
                'b2': np.random.randn(1, 1),
                'input_size': 4,
                'hidden_size': 8
            }
            np.savez(os.path.join(working_model_dir, "stock_model.npz"), **mock_weights)
            
            # Create feature info
            feature_info = {
                'x_features': ['open', 'high', 'low', 'vol'],
                'y_feature': 'close',
                'model_type': 'basic',
                'training_params': {'hidden_size': 8}
            }
            
            with open(os.path.join(working_model_dir, "feature_info.json"), 'w') as f:
                json.dump(feature_info, f)
            
            # Test prediction parameters
            params = {
                'model_path': empty_model_dir,
                'data_file': data_file
            }
            
            # The enhanced search should find the working model
            model_file = prediction_integration._find_model_file_enhanced(empty_model_dir)
            
            if model_file and "stock_model.npz" in model_file:
                print("✅ Enhanced search found working model for prediction")
                print(f"Found: {model_file}")
            else:
                print("❌ Enhanced search failed to find working model for prediction")
                return False
        
        print("\n✅ All tests passed! Enhanced prediction functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_prediction()
    if success:
        print("\n🎉 Enhanced prediction test completed successfully!")
    else:
        print("\n💥 Enhanced prediction test failed!")
        sys.exit(1) 