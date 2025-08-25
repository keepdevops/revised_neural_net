#!/usr/bin/env python3
"""
Test Model Validation Fix
This test verifies that the model validation logic correctly identifies valid models.
"""

import os
import sys
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestModelValidationFix:
    """Test class for model validation fix."""
    
    def __init__(self):
        self.test_models = [
            "/Users/porupine/Desktop/revised_neural_net/model_20250628_122008",
            "/Users/porupine/Desktop/revised_neural_net/model_20250628_121401"
        ]
    
    def test_model_validation(self):
        """Test the model validation logic."""
        logger.info("Testing model validation fix...")
        
        # Import the prediction panel to test its validation method
        try:
            from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
            
            # Create a mock app object
            class MockApp:
                def __init__(self):
                    self.selected_model = None
                    self.current_data_file = None
                    self.prediction_batch_size = 32
                    self.prediction_confidence = 0.8
            
            mock_app = MockApp()
            
            # Create a mock parent
            class MockParent:
                def __init__(self):
                    pass
            
            mock_parent = MockParent()
            
            # Create prediction panel instance
            prediction_panel = PredictionPanel(mock_parent, mock_app)
            
            # Test each model
            for model_path in self.test_models:
                logger.info(f"Testing model: {model_path}")
                
                # Check if directory exists
                if not os.path.exists(model_path):
                    logger.warning(f"Model directory does not exist: {model_path}")
                    continue
                
                # List files in the model directory
                files = os.listdir(model_path)
                logger.info(f"Files in {os.path.basename(model_path)}: {files}")
                
                # Test the validation method
                is_valid = prediction_panel._has_valid_model_files(model_path)
                logger.info(f"Model validation result: {is_valid}")
                
                if is_valid:
                    logger.info(f"✅ Model {os.path.basename(model_path)} is valid")
                else:
                    logger.warning(f"❌ Model {os.path.basename(model_path)} is invalid")
                
                print(f"Model: {os.path.basename(model_path)} - Valid: {is_valid}")
            
            logger.info("Model validation test completed")
            
        except Exception as e:
            logger.error(f"Error testing model validation: {e}")
            import traceback
            traceback.print_exc()
    
    def run_tests(self):
        """Run all tests."""
        logger.info("Starting model validation fix tests...")
        self.test_model_validation()
        logger.info("All tests completed")

def main():
    """Main test function."""
    test = TestModelValidationFix()
    test.run_tests()

if __name__ == "__main__":
    main() 