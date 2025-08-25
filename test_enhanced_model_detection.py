#!/usr/bin/env python3
"""
Test script to verify enhanced model file detection in prediction integration.
"""

import os
import sys
import tempfile
import json
import numpy as np

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_enhanced_model_detection():
    """Test the enhanced model file detection functionality."""
    print("🧪 Testing Enhanced Model File Detection")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.prediction_integration import PredictionIntegration
        
        # Create a mock app object
        class MockApp:
            def __init__(self):
                self.data_manager = None
        
        app = MockApp()
        prediction_integration = PredictionIntegration(app)
        
        # Test 1: Test enhanced model file search with empty directory
        print("\n1️⃣ Testing enhanced model file search with empty directory...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an empty model directory
            empty_model_dir = os.path.join(temp_dir, "empty_model")
            os.makedirs(empty_model_dir, exist_ok=True)
            
            # Test the enhanced search
            model_file = prediction_integration._find_model_file_enhanced(empty_model_dir)
            
            if model_file is None:
                print("✅ Enhanced search correctly returned None for empty directory")
            else:
                print(f"❌ Enhanced search unexpectedly found file: {model_file}")
                return False
        
        # Test 2: Test error message generation
        print("\n2️⃣ Testing error message generation...")
        
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
        
        # Test 3: Test with actual model files in parent directory
        print("\n3️⃣ Testing with actual model files in parent directory...")
        
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
        
        print("\n✅ All tests passed! Enhanced model file detection is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_model_detection()
    if success:
        print("\n🎉 Enhanced model file detection test completed successfully!")
    else:
        print("\n💥 Enhanced model file detection test failed!")
        sys.exit(1) 