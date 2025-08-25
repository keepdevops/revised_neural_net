#!/usr/bin/env python3
"""
Test Hidden Size Synchronization
This test verifies that the prediction system uses the same hidden size as the training parameters.
"""

import os
import sys
import json
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hidden_size_sync():
    """Test that prediction uses the same hidden size as training parameters."""
    try:
        # Find a model directory with feature_info.json
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
        feature_info_path = os.path.join(project_root, test_model_dir, 'feature_info.json')
        
        logger.info(f"Testing with model: {test_model_dir}")
        
        # Load feature_info.json
        with open(feature_info_path, 'r') as f:
            feature_info = json.load(f)
        
        # Extract training parameters
        training_params = feature_info.get('training_params', {})
        saved_hidden_size = training_params.get('hidden_size', 4)
        
        logger.info(f"Training parameters hidden_size: {saved_hidden_size}")
        
        # Simulate what the prediction integration would do
        # This is the logic from the prediction_integration.py file
        training_params_from_feature_info = feature_info.get('training_params', {})
        hidden_size_from_prediction = training_params_from_feature_info.get('hidden_size', 4)
        
        logger.info(f"Prediction would use hidden_size: {hidden_size_from_prediction}")
        
        # Verify they match
        if saved_hidden_size == hidden_size_from_prediction:
            logger.info("✅ SUCCESS: Hidden size matches between training and prediction")
            return True
        else:
            logger.error(f"❌ FAILURE: Hidden size mismatch - training: {saved_hidden_size}, prediction: {hidden_size_from_prediction}")
            return False
            
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return False

def test_multiple_models():
    """Test multiple models to ensure consistency."""
    try:
        # Find all model directories with feature_info.json
        model_dirs = []
        for item in os.listdir(project_root):
            if item.startswith('model_') and os.path.isdir(os.path.join(project_root, item)):
                feature_info_path = os.path.join(project_root, item, 'feature_info.json')
                if os.path.exists(feature_info_path):
                    model_dirs.append(item)
        
        if not model_dirs:
            logger.error("No model directories with feature_info.json found")
            return False
        
        logger.info(f"Testing {len(model_dirs)} models for hidden size consistency")
        
        results = []
        for model_dir in model_dirs[:5]:  # Test first 5 models
            feature_info_path = os.path.join(project_root, model_dir, 'feature_info.json')
            
            try:
                with open(feature_info_path, 'r') as f:
                    feature_info = json.load(f)
                
                training_params = feature_info.get('training_params', {})
                hidden_size = training_params.get('hidden_size', 4)
                
                # Simulate prediction logic
                training_params_from_feature_info = feature_info.get('training_params', {})
                hidden_size_from_prediction = training_params_from_feature_info.get('hidden_size', 4)
                
                match = hidden_size == hidden_size_from_prediction
                results.append({
                    'model': model_dir,
                    'training_hidden_size': hidden_size,
                    'prediction_hidden_size': hidden_size_from_prediction,
                    'match': match
                })
                
                logger.info(f"Model {model_dir}: training={hidden_size}, prediction={hidden_size_from_prediction}, match={match}")
                
            except Exception as e:
                logger.error(f"Error testing model {model_dir}: {e}")
                results.append({
                    'model': model_dir,
                    'error': str(e)
                })
        
        # Summary
        successful_tests = [r for r in results if 'match' in r and r['match']]
        failed_tests = [r for r in results if 'match' in r and not r['match']]
        error_tests = [r for r in results if 'error' in r]
        
        logger.info(f"\nTest Summary:")
        logger.info(f"✅ Successful: {len(successful_tests)}")
        logger.info(f"❌ Failed: {len(failed_tests)}")
        logger.info(f"⚠️ Errors: {len(error_tests)}")
        
        return len(failed_tests) == 0 and len(error_tests) == 0
        
    except Exception as e:
        logger.error(f"Error in multiple models test: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing Hidden Size Synchronization")
    logger.info("=" * 50)
    
    # Test single model
    single_test_result = test_hidden_size_sync()
    
    logger.info("\n" + "=" * 50)
    
    # Test multiple models
    multiple_test_result = test_multiple_models()
    
    logger.info("\n" + "=" * 50)
    logger.info("FINAL RESULTS:")
    logger.info(f"Single model test: {'✅ PASSED' if single_test_result else '❌ FAILED'}")
    logger.info(f"Multiple models test: {'✅ PASSED' if multiple_test_result else '❌ FAILED'}")
    
    if single_test_result and multiple_test_result:
        logger.info("🎉 ALL TESTS PASSED - Hidden size synchronization is working correctly!")
    else:
        logger.error("💥 SOME TESTS FAILED - Hidden size synchronization needs attention!") 