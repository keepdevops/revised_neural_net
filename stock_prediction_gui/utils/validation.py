"""
Validation utilities for the Stock Prediction GUI.
"""

import os
import logging

class ValidationUtils:
    """Utility class for input validation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_training_params(self, params):
        """Validate training parameters."""
        try:
            required_fields = ['data_file', 'output_dir', 'x_features', 'y_feature']
            
            for field in required_fields:
                if field not in params or not params[field]:
                    self.logger.error(f"Missing required parameter: {field}")
                    return False
            
            # Validate file exists
            if not os.path.exists(params['data_file']):
                self.logger.error(f"Data file not found: {params['data_file']}")
                return False
            
            # Validate output directory
            if not os.path.exists(params['output_dir']):
                try:
                    os.makedirs(params['output_dir'], exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Cannot create output directory: {e}")
                    return False
            
            # Validate features
            if not isinstance(params['x_features'], list) or len(params['x_features']) == 0:
                self.logger.error("No input features specified")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating training parameters: {e}")
            return False
    
    def validate_prediction_params(self, params):
        """Validate prediction parameters."""
        try:
            required_fields = ['model_path', 'data_file']
            
            for field in required_fields:
                if field not in params or not params[field]:
                    self.logger.error(f"Missing required parameter: {field}")
                    return False
            
            # Validate files exist
            if not os.path.exists(params['model_path']):
                self.logger.error(f"Model path not found: {params['model_path']}")
                return False
            
            if not os.path.exists(params['data_file']):
                self.logger.error(f"Data file not found: {params['data_file']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating prediction parameters: {e}")
            return False
    
    def validate_data_file(self, file_path):
        """Validate data file."""
        if not file_path:
            return False, "No file path provided"
        
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file extension
        if not file_path.lower().endswith('.csv'):
            return False, "File must be a CSV file"
        
        return True, ""
    
    def validate_model_directory(self, model_dir):
        """Validate model directory."""
        if not model_dir:
            return False, "No model directory provided"
        
        if not os.path.exists(model_dir):
            return False, "Model directory does not exist"
        
        # Check for required files
        required_files = ['feature_info.json']
        missing_files = []
        
        for file_name in required_files:
            file_path = os.path.join(model_dir, file_name)
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        if missing_files:
            return False, f"Missing required files: {missing_files}"
        
        return True, "" 