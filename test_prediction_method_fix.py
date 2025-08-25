#!/usr/bin/env python3
"""
Test Prediction Method Fix
This test verifies that the prediction system can now make predictions correctly.
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

def test_stocknet_prediction():
    """Test that StockNet models can make predictions using the forward method."""
    try:
        # Import StockNet
        from stock_net import StockNet
        
        # Create a simple test model
        input_size = 4
        hidden_size = 4
        model = StockNet(input_size, hidden_size)
        
        # Create test data
        X_test = np.random.randn(10, input_size)
        
        # Test that forward method works
        predictions = model.forward(X_test)
        
        logger.info(f"✅ SUCCESS: StockNet forward method works")
        logger.info(f"Input shape: {X_test.shape}")
        logger.info(f"Output shape: {predictions.shape}")
        logger.info(f"Predictions range: {predictions.min():.4f} to {predictions.max():.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILURE: StockNet forward method failed: {e}")
        return False

def test_model_loading_and_prediction():
    """Test loading a model and making predictions."""
    try:
        # Find a model directory
        model_dirs = []
        for item in os.listdir(project_root):
            if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
                feature_info_path = os.path.join(project_root, item, 'feature_info.json')
                if os.path.exists(feature_info_path):
                    model_dirs.append(item)
        
        if not model_dirs:
            logger.error("No model directories with feature_info.json found")
            return False
        
        # Test with the first available model
        test_model_dir = model_dirs[0]
        logger.info(f"Testing with model: {test_model_dir}")
        
        # Import StockNet
        from stock_net import StockNet
        
        # Load the model
        model = StockNet.load_weights(os.path.join(project_root, test_model_dir))
        
        # Create test data based on the model's input size
        input_size = model.W1.shape[0]
        X_test = np.random.randn(5, input_size)
        
        # Make predictions using forward method
        predictions = model.forward(X_test)
        
        logger.info(f"✅ SUCCESS: Model loading and prediction works")
        logger.info(f"Model input size: {input_size}")
        logger.info(f"Test input shape: {X_test.shape}")
        logger.info(f"Predictions shape: {predictions.shape}")
        logger.info(f"Predictions range: {predictions.min():.4f} to {predictions.max():.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILURE: Model loading and prediction failed: {e}")
        return False

def test_prediction_integration_simulation():
    """Simulate the prediction integration logic."""
    try:
        # Find a model directory
        model_dirs = []
        for item in os.listdir(project_root):
            if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
                feature_info_path = os.path.join(project_root, item, 'feature_info.json')
                if os.path.exists(feature_info_path):
                    model_dirs.append(item)
        
        if not model_dirs:
            logger.error("No model directories with feature_info.json found")
            return False
        
        # Test with the first available model
        test_model_dir = model_dirs[0]
        logger.info(f"Testing prediction integration simulation with model: {test_model_dir}")
        
        # Import StockNet
        from stock_net import StockNet
        
        # Load the model
        model = StockNet.load_weights(os.path.join(project_root, test_model_dir))
        
        # Create test data
        input_size = model.W1.shape[0]
        X_test = np.random.randn(10, input_size)
        
        # Simulate the prediction integration logic
        batch_size = 32
        total_samples = len(X_test)
        predictions = []
        
        # Process in batches (simulating the integration logic)
        for i in range(0, total_samples, batch_size):
            batch_end = min(i + batch_size, total_samples)
            X_batch = X_test[i:batch_end]
            
            # Make prediction for this batch using forward method
            batch_predictions = model.forward(X_batch)
            predictions.extend(batch_predictions.flatten())
        
        predictions = np.array(predictions)
        
        logger.info(f"✅ SUCCESS: Prediction integration simulation works")
        logger.info(f"Total samples: {total_samples}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Predictions shape: {predictions.shape}")
        logger.info(f"Predictions range: {predictions.min():.4f} to {predictions.max():.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILURE: Prediction integration simulation failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing Prediction Method Fix")
    logger.info("=" * 50)
    
    # Test 1: Basic StockNet prediction
    test1_result = test_stocknet_prediction()
    
    logger.info("\n" + "=" * 50)
    
    # Test 2: Model loading and prediction
    test2_result = test_model_loading_and_prediction()
    
    logger.info("\n" + "=" * 50)
    
    # Test 3: Prediction integration simulation
    test3_result = test_prediction_integration_simulation()
    
    logger.info("\n" + "=" * 50)
    logger.info("FINAL RESULTS:")
    logger.info(f"Basic StockNet prediction: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    logger.info(f"Model loading and prediction: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    logger.info(f"Prediction integration simulation: {'✅ PASSED' if test3_result else '❌ FAILED'}")
    
    if test1_result and test2_result and test3_result:
        logger.info("🎉 ALL TESTS PASSED - Prediction method fix is working correctly!")
    else:
        logger.error("💥 SOME TESTS FAILED - Prediction method fix needs attention!") 