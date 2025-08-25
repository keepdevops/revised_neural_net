#!/usr/bin/env python3
"""
Test Prediction Fix
This test verifies that the prediction system can now load models correctly.
"""

import os
import sys
import logging
import numpy as np

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test that models can be loaded correctly."""
    try:
        # Test with a known model directory
        model_dir = "/Users/porupine/Desktop/revised_neural_net/model_20250628_203753"
        
        if not os.path.exists(model_dir):
            logger.error(f"Model directory not found: {model_dir}")
            return False
        
        # Check if the model file exists
        model_file = os.path.join(model_dir, "stock_model.npz")
        if not os.path.exists(model_file):
            logger.error(f"Model file not found: {model_file}")
            return False
        
        # Test loading the model using StockNet.load_weights
        from stock_net import StockNet
        
        logger.info("Testing StockNet.load_weights class method...")
        model = StockNet.load_weights(model_dir, prefix="stock_model")
        
        # Verify the model has the expected attributes
        if not hasattr(model, 'W1') or not hasattr(model, 'W2'):
            logger.error("Loaded model missing weight attributes")
            return False
        
        if not hasattr(model, 'b1') or not hasattr(model, 'b2'):
            logger.error("Loaded model missing bias attributes")
            return False
        
        logger.info(f"Model loaded successfully!")
        logger.info(f"W1 shape: {model.W1.shape}")
        logger.info(f"W2 shape: {model.W2.shape}")
        logger.info(f"b1 shape: {model.b1.shape}")
        logger.info(f"b2 shape: {model.b2.shape}")
        
        # Test making a prediction
        logger.info("Testing model prediction...")
        test_input = np.random.randn(10, model.W1.shape[0])  # 10 samples with correct input size
        prediction = model.forward(test_input)
        logger.info(f"Prediction shape: {prediction.shape}")
        logger.info(f"Prediction successful!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing model loading: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_integration():
    """Test the prediction integration module."""
    try:
        from stock_prediction_gui.core.prediction_integration import PredictionIntegration
        
        # Create a mock app for testing
        class MockApp:
            def __init__(self):
                self.data_manager = None
                self.prediction_batch_size = 32
        
        mock_app = MockApp()
        prediction_integration = PredictionIntegration(mock_app)
        
        logger.info("Prediction integration module loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing prediction integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    logger.info("Starting prediction fix tests...")
    
    # Test 1: Model loading
    logger.info("\n=== Test 1: Model Loading ===")
    if test_model_loading():
        logger.info("✅ Model loading test passed")
    else:
        logger.error("❌ Model loading test failed")
        return False
    
    # Test 2: Prediction integration
    logger.info("\n=== Test 2: Prediction Integration ===")
    if test_prediction_integration():
        logger.info("✅ Prediction integration test passed")
    else:
        logger.error("❌ Prediction integration test failed")
        return False
    
    logger.info("\n🎉 All tests passed! The prediction fix is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 