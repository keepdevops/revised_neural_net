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
        
        # Check for model files (weights) - these are required
        model_files = ['stock_model.npz', 'model.npz', 'final_model.npz', 'best_model.npz']
        has_model_file = any(os.path.exists(os.path.join(model_dir, f)) for f in model_files)
        
        # If no main model file found, check weights_history directory
        if not has_model_file:
            weights_history_dir = os.path.join(model_dir, 'weights_history')
            if os.path.exists(weights_history_dir):
                weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
                if weight_files:
                    has_model_file = True
        
        if not has_model_file:
            return False, "No model weights file found (stock_model.npz, model.npz, final_model.npz, best_model.npz, or weight files in weights_history/)"
        
        # Check for feature info (optional but preferred)
        feature_info_path = os.path.join(model_dir, 'feature_info.json')
        if not os.path.exists(feature_info_path):
            # Warning but not error - we can auto-detect features
            self.logger.warning(f"No feature_info.json found in {model_dir}. Features will be auto-detected from data.")
        
        return True, "" 