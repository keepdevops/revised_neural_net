#!/usr/bin/env python3
"""
Simple Model Validation Test
This test directly tests the model validation logic without requiring Tkinter.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def has_valid_model_files(model_dir):
    """Check if model directory has valid model files - simplified version."""
    try:
        # Check for essential files - updated to match actual model structure
        required_files = ['stock_model.npz', 'feature_info.json']
        optional_files = ['weights_history', 'plots', 'training_data.csv', 'training_losses.csv']
        
        # Check if all required files exist
        for file in required_files:
            if not os.path.exists(os.path.join(model_dir, file)):
                logger.debug(f"Missing required file: {file} in {model_dir}")
                return False
        
        # Check if at least one optional directory or file exists
        has_optional = any(os.path.exists(os.path.join(model_dir, file)) for file in optional_files)
        
        if not has_optional:
            logger.debug(f"No optional files found in {model_dir}")
        
        return has_optional
        
    except Exception as e:
        logger.error(f"Error checking model files: {e}")
        return False

def test_model_validation():
    """Test the model validation logic."""
    logger.info("Testing model validation fix...")
    
    test_models = [
        "/Users/porupine/Desktop/revised_neural_net/model_20250628_122008",
        "/Users/porupine/Desktop/revised_neural_net/model_20250628_121401"
    ]
    
    # Test each model
    for model_path in test_models:
        logger.info(f"Testing model: {model_path}")
        
        # Check if directory exists
        if not os.path.exists(model_path):
            logger.warning(f"Model directory does not exist: {model_path}")
            continue
        
        # List files in the model directory
        files = os.listdir(model_path)
        logger.info(f"Files in {os.path.basename(model_path)}: {files}")
        
        # Test the validation method
        is_valid = has_valid_model_files(model_path)
        logger.info(f"Model validation result: {is_valid}")
        
        if is_valid:
            logger.info(f"✅ Model {os.path.basename(model_path)} is valid")
        else:
            logger.warning(f"❌ Model {os.path.basename(model_path)} is invalid")
        
        print(f"Model: {os.path.basename(model_path)} - Valid: {is_valid}")
    
    logger.info("Model validation test completed")

def main():
    """Main test function."""
    logger.info("Starting simple model validation test...")
    test_model_validation()
    logger.info("Test completed")

if __name__ == "__main__":
    main() 